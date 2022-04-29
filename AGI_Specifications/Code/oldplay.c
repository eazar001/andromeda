/**************************************************************************
** play.c
**
** Plays AGI sounds.
**
** Written by: Lance Ewing
**************************************************************************/

#include <stdio.h>
#include <conio.h>
#include <dos.h>

#include "adlib.h"

#define TRUE  1
#define FALSE 0

typedef unsigned char byte;
typedef unsigned int word;
typedef char boolean;

typedef struct {
   int firstPart, secondPart, thirdPart, endOfMusic;
} SNDHeader;

typedef struct {
   word duration;
   byte noteHi, noteLo, maxNoteLo;
} noteType;

typedef struct {
   float frequency;
   int durationLeft;
} currentNoteType;

typedef struct {
   currentNoteType firstPartNote, secondPartNote, thirdPartNote;
} currentNotesType;

typedef struct {
   float stopFreq;
   float freqMult;
} blockDataType;

static blockDataType blockData[8] = {
   { 48.50336838, 21.09131869 },
   { 97.00673676, 10.54565935 },
   { 194.0134735, 5.272829673 },
   { 388.026947,  2.636414836 },
   { 776.053894,  1.318207418 },
   { 1552.107788, 0.659103709 },
   { 3104.215576, 0.329551854 },
   { 6208.431152, 0.164775927 }
};

int delNum=18;
boolean speakerPlay = FALSE, adlibPlay = FALSE;


/**************************************************************************
** playFrequency
**
** Plays the given frequency over the adlib voice specified.
**************************************************************************/
void playFrequency(byte voice, float freq)
{
   int blockNum, fNum;

   for (blockNum=0; blockNum<8; blockNum++) {
      if (freq < blockData[blockNum].stopFreq) {
	 fNum = (int)(freq*blockData[blockNum].freqMult);
	 FMKeyOn(voice, fNum, blockNum);
	 break;
      }
   }
}

/**************************************************************************
** noteConvert
**
** Converts the note data given in the SOUND file to a frequency.
**************************************************************************/
float noteConvert(byte noteHi, byte noteLo, byte maxNoteLo)
{
   int fileData;

   fileData = ((noteHi & 0x3F) << 4) + (noteLo & 0x0F);
   if (noteHi == 0)
      return 0;
   else
      return (99320/fileData);
}

/**************************************************************************
** readNote
**
** Reads a note from the SOUND file and returns it in the form that the
** program requires it in.
**************************************************************************/
void readNote(FILE *SNDFile, currentNoteType *note, int *placer)
{
   noteType noteData;

   fseek(SNDFile, (long) *placer, SEEK_SET);
   fread(&noteData, 1, sizeof(noteType), SNDFile);

   note->durationLeft = noteData.duration;
   note->frequency = noteConvert(noteData.noteHi, noteData.noteLo,
      noteData.maxNoteLo);

   *placer += 5;
}

/**************************************************************************
** playTune
**
** Plays the tune contained in the SOUND file.
**************************************************************************/
void playTune(FILE *SNDFile)
{
   currentNotesType currentNoteData;
   SNDHeader partOffsets;
   int placer1, placer2, placer3;
   char ch;
   boolean stillPlaying = TRUE;


/* Read SND file header */

   fread(&partOffsets, 1, sizeof(SNDHeader), SNDFile);


/* Set up placers for each part */

   placer1 = partOffsets.firstPart;
   placer2 = partOffsets.secondPart;
   placer3 = partOffsets.thirdPart;


   currentNoteData.firstPartNote.durationLeft = 0;
   currentNoteData.secondPartNote.durationLeft = 0;
   currentNoteData.thirdPartNote.durationLeft = 0;


/*************************************************************************
** MAIN LOOP
*************************************************************************/

   while (stillPlaying) {

      /* Check if the notes have timed out */

      if (currentNoteData.firstPartNote.durationLeft <= 0) {
	 readNote(SNDFile, &currentNoteData.firstPartNote, &placer1);
	 if (adlibPlay) {
	    FMKeyOff(0);
	    playFrequency(0, currentNoteData.firstPartNote.frequency);
	 }
	 if (speakerPlay) {
	    nosound();
	    sound(currentNoteData.firstPartNote.frequency);
	 }
      }

      if (currentNoteData.secondPartNote.durationLeft <= 0) {
	 readNote(SNDFile, &currentNoteData.secondPartNote, &placer2);
	 if (adlibPlay) {
	    FMKeyOff(1);
	    playFrequency(1, currentNoteData.secondPartNote.frequency);
	 }
      }

      if (currentNoteData.thirdPartNote.durationLeft <= 0) {
	 readNote(SNDFile, &currentNoteData.thirdPartNote, &placer3);
	 if (adlibPlay) {
	    FMKeyOff(2);
	    playFrequency(2, currentNoteData.thirdPartNote.frequency);
	 }
      }

      delay(delNum);

      /* Reduce all note durations by 1 */

      currentNoteData.firstPartNote.durationLeft--;
      currentNoteData.secondPartNote.durationLeft--;
      currentNoteData.thirdPartNote.durationLeft--;


      if ((placer1 > (partOffsets.secondPart - 2)) ||
	  (placer2 > (partOffsets.thirdPart - 2)) ||
	  (placer3 > (partOffsets.endOfMusic - 2))) { stillPlaying = FALSE; }


      if (kbhit()) stillPlaying = FALSE;
   }


   if (adlibPlay) {
      FMKeyOff(0);
      FMKeyOff(1);
      FMKeyOff(2);
      FMReset();
   }

   if (speakerPlay) nosound();
}

/**************************************************************************
** initSoundcard
**
** Initialises the sound card if the user has specified output over the
** adlib or soundblaster.
**************************************************************************/
void initSoundcard()
{
   int voice;
   FMInstrument lowInst =
   {
      0x21, 0x31, 0x4E, 0x00,
      0xF1, 0xF1, 0x11, 0x11,
      0x00, 0x00, 0x06
   };

   FMReset();

   for (voice=0; voice<3; voice++) {
      FMSetVoice(voice, &lowInst);
      FMSetVolume(voice, 0);
   }
}

/**************************************************************************
** main
**************************************************************************/
void main(int argc, char **argv)
{
   FILE *SNDFile;
   byte opt;

   if (argc < 2) {
      printf("Usage: play filename\n");
      printf("\n-a  adlib/sound blaster\n");
      printf("-s  PC speaker\n");
      exit(0);
   }
   else {
      for (opt=1; opt!=(argc-1); opt++) {
	 if (argv[opt][0] == '-') {
	    switch(argv[opt][1]) {
	       case 's': speakerPlay = TRUE; break;
	       case 'a': adlibPlay = TRUE; break;
	       default: printf("Illegal option : %s\n", argv[opt]); exit(0);
	    }
	 }
	 else {
	    printf("Illegal option : %s\n", argv[opt]);
	    exit(0);
	 }
      }

      if (!speakerPlay && !adlibPlay) {
	 printf("Must select either adlib/SB or PC speaker or both.\n");
	 exit(0);
      }

      if ((SNDFile = fopen(argv[argc-1], "rb")) == NULL) {
	 printf("Error opening file : %s\n", argv[argc-1]);
	 exit(0);
      }
   }


   if (adlibPlay) initSoundcard();
   playTune(SNDFile);

   fclose(SNDFile);
}

