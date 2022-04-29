/* C Source File: ADLIB *****************************************************

Author:             Kevin A. Lee

Last Amended:       27th March, 1993

Description:        Low-level interface to the Adlib (or compatible)
FM sound card. All information gleaned from
Jeffrey S. Lee's "Programming the Adlib/Sound
Blaster FM Music Chips". See Lee's document for
further information.
Compiled succesfully under Turbo C, Borland C++,
and Microsoft Quick C (all latest versions).

****************************************************************************/

#include <stdio.h>
#include <conio.h>
#include <time.h>
#include <dos.h>
#include "adlib.h"

/* local function */
void Wait(clock_t wait);

/* Function: WriteFM ********************************************************
*
*      Parameters:         reg - which FM register to write to.
*                          value - value to write.
*
*      Description:        writes a value to the specified register and
*                          waits for the "official" recommended periods.
*
*/
void WriteFM(int reg, int value)
{
   int i;

   outp(ADLIB_FM_ADDRESS, (BYTE)reg);              /* set up the register  */
   for (i = 0; i < 6; i++) inp(ADLIB_FM_ADDRESS);  /* wait 12 cycles       */
   outp(ADLIB_FM_DATA, (BYTE)value);               /* write out the value  */
   for (i = 0; i < 35; i++) inp(ADLIB_FM_ADDRESS); /* wait 84 cycles       */

} /* End of WriteFM */



/* Function: ReadFM *********************************************************
*
*      Returns:            the value in the status register.
*
*      Description:        return a value in the status register.
*
*/
int ReadFM(void)
{
   return (inp(ADLIB_FM_ADDRESS));

} /* End of ReadFM */



/* Function: AdlibExists ****************************************************
*
*      Returns:            1 (true) if an Adlib compatible sound card
*                          is present, else 0 (false).
*
*      Description:        determines whether an Adlib (or compatible)
*                          sound card is present.
*
*/
int AdlibExists(void)
{
   int stat1, stat2;

   WriteFM(0x04, 0x60);            /* reset both timers        */
   WriteFM(0x04, 0x80);            /* enable timer interrupts  */
   stat1 = ReadFM();               /* read status register     */
   WriteFM(0x02, 0xFF);
   WriteFM(0x04, 0x21);            /* start timer 1            */
   Wait(10);                       /* could do something useful*/
   stat2 = ReadFM();               /* read status register     */
   WriteFM(0x04, 0x60);            /* reset both timers        */
   WriteFM(0x04, 0x80);            /* enable timer interrupts  */

   if (((stat1 & 0xE0) == 0x00) && ((stat2 & 0xE0) == 0xC0)) return (1);
   return (0);

} /* End of AdlibExists */



/* Function: FMResest *******************************************************
*
*      Description:        quick and dirty sound card reset (zeros all
*                          registers).
*
*/
void FMReset(void)
{
   int i;

   /* zero all registers */
   for (i = MIN_REGISTER; i < MAX_REGISTER+1; i++) WriteFM(i, 0);

   /* allow FM chips to control the waveform of each operator */
   WriteFM(0x01, 0x20);

   /* set rhythm enabled (6 melodic voices, 5 percussive) */
   WriteFM(0xBD, 0x20);

} /* End of FMReset */



/* Function: FMKeyOff *******************************************************
*
*      Parameters:         voice - which voice to turn off.
*
*      Description:        turns off the specified voice.
*
*/
void FMKeyOff(int voice)
{
   int regNum;

   /* turn voice off */
   regNum = 0xB0 + voice % 11;
   WriteFM(regNum, 0);

} /* End of FMKeyOff */



/* Function: FMKeyOn ********************************************************
*
*      Parameters:         voice - which voice to turn on.
*                          freq - its frequency (note).
*                          octave - its octave.
*
*      Description:        turns on a voice of specfied frequency and
*                          octave.
*
*/
void FMKeyOn(int voice, int freq, int octave)
{
   int regNum, tmp;

   regNum = 0xA0 + voice % 11;
   WriteFM(regNum, freq & 0xff);
   regNum = 0xB0 + voice % 11;
   tmp = (freq >> 8) | (octave << 2) | 0x20;
   WriteFM(regNum, tmp);

} /* End of FMKeyOn */


/* Function: FMVoiceVolume **************************************************
*
*      Parameters:         voice - which voice to set volume of
*                          vol - new volume value (experiment).
*
*      Description:        sets the volume of a voice to the specified
*                          value in the range (0-63)?
*
*/
void FMVoiceVolume(int voice, int vol)
{
   int regNum;

   regNum = 0x40 + voice % 11;
   WriteFM(regNum, vol);

} /* End of FMVoiceVolume */



/* Function: FMSetVoice *****************************************************
*
*      Parameters:         voiceNum - which voice to set.
*                          ins - instrument to set voice.
*
*      Description:        sets the instrument of a voice.
*
*/
void FMSetVoice(int voiceNum, FMInstrument *ins)
{
   int opCellNum, cellOffset, i;

   voiceNum %= 11;
   cellOffset = voiceNum % 3 + ((voiceNum / 3) << 3);

   /* set sound characteristic */
   opCellNum = 0x20 + (char)cellOffset;
   WriteFM(opCellNum, ins->SoundCharacteristic[0]);
   opCellNum += 3;
   WriteFM(opCellNum, ins->SoundCharacteristic[1]);

   /* set level/output */
   opCellNum = 0x40 + (char)cellOffset;
   WriteFM(opCellNum, ins->Level[0]);
   opCellNum += 3;
   WriteFM(opCellNum, ins->Level[1]);

   /* set Attack/Decay */
   opCellNum = 0x60 + (char)cellOffset;
   WriteFM(opCellNum, ins->AttackDecay[0]);
   opCellNum += 3;
   WriteFM(opCellNum, ins->AttackDecay[1]);

   /* set Sustain/Release */
   opCellNum = 0x80 + (char)cellOffset;
   WriteFM(opCellNum, ins->SustainRelease[0]);
   opCellNum += 3;
   WriteFM(opCellNum, ins->SustainRelease[1]);

   /* set Wave Select */
   opCellNum = 0xE0 + (char)cellOffset;
   WriteFM(opCellNum, ins->WaveSelect[0]);
   opCellNum += 3;
   WriteFM(opCellNum, ins->WaveSelect[1]);

   /* set Feedback/Selectivity */
   opCellNum = (BYTE)0xC0 + (BYTE)voiceNum;
   WriteFM(opCellNum, ins->Feedback);

} /* End of FMSetVoice */



/* Function: LoadSBI ********************************************************
*
*      Parameters:         fileName - name of .SBI file.
*                          ins - variable to place data in.
*
*      Description:        loads a .SBI into the instrument structure.
*
*/
int LoadSBI(char fileName[], FMInstrument *ins)
{
   int i;
   FILE *fp;
   size_t structSize = sizeof(FMInstrument);

   if ((fp = fopen(fileName, "rb")) == NULL) return (0);

   /* skip the header - or do we? */
   for (i = 0; i < 36; i++) fgetc(fp);

   /* read the data */
   fread(ins, structSize, 1, fp);

   fclose(fp);
   return (1);

} /* End of LoadSBI */


void FMSetVolume(int voiceNum, int vol)
{
   int opCellNum, cellOffset;

   voiceNum %= 11;
   cellOffset = voiceNum % 3 + ((voiceNum / 3) << 3);
   opCellNum = 0x40 + (char)cellOffset;
   opCellNum += 3;
   WriteFM(opCellNum, vol);
}


/* Function: Wait **********************************************************
*
*      Parameters:     wait - time in microseconds
*
*      Description:    pauses for a specified number of microseconds.
*
*/
void Wait(clock_t wait)
{
   clock_t goal;

   if (!wait) return;

   goal = wait + clock();
   while ((goal > clock()) && !kbhit()) ;

} /* End of Wait */