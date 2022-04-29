/***************************************************************************
** AGIFILES.C
**
** Routines to handle AGI file system. These functions should enable you
** to load individual LOGIC, VIEW, PIC, and SOUND files into memory. The
** data is stored in a structure of type AGIFile. There is no code that
** is specific to the above types of data file though.
**
** (c) 1997 Lance Ewing
***************************************************************************/

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "agifiles.h"

#define  EMPTY  0xFFFFF   /* Empty DIR entry */


AGIFilePosType logdir[256], picdir[256], viewdir[256], snddir[256];
int numLogics, numPictures, numViews, numSounds;

/***************************************************************************
** loadAGIDir
**
** Purpose: To read in an individual AGI directory file. This function
** should only be called by loadAGIDirs() below.
***************************************************************************/
void loadAGIDir(int dirNum, char *fName, int *count)
{
   FILE *fp;
   unsigned char byte1, byte2, byte3;
   AGIFilePosType tempPos;
   fpos_t pos;

   if ((fp = fopen(fName, "rb")) == NULL) {
      printf("Could not find file : %s.\n", fName);
      printf("Make sure you are in an AGI version 2 game directory.\n");
      exit(0);
   }

   while (!feof(fp)) {
      byte1 = fgetc(fp);
      byte2 = fgetc(fp);
      byte3 = fgetc(fp);

      fgetpos(fp, &pos);

      tempPos.fileName = (char *)malloc(10);
      sprintf(tempPos.fileName, "VOL.%d", ((byte1 & 0xF0) >> 4));
      tempPos.filePos = ((long)((byte1 & 0x0F) << 16) +
                         (long)((byte2 & 0xFF) << 8) +
                         (long)(byte3 & 0xFF));

      switch (dirNum) {
         case 0: logdir[*count] = tempPos; break;
         case 1: picdir[*count] = tempPos; break;
         case 2: viewdir[*count] = tempPos; break;
         case 3: snddir[*count] = tempPos; break;
      }
      (*count)++;
   }

   fclose(fp);
}

/***************************************************************************
** loadAGIDirs
**
** Purpose: To read the AGI directory files LOGDIR, PICDIR, VIEWDIR, and
** SNDDIR and store the information in a usable format. This function must
** be called once at the start of the interpreter.
***************************************************************************/
void loadAGIDirs()
{
   numLogics = numPictures = numViews = numSounds = 0;
   loadAGIDir(0, "LOGDIR", &numLogics);
   loadAGIDir(1, "PICDIR", &numPictures);
   loadAGIDir(2, "VIEWDIR", &numViews);
   loadAGIDir(3, "SNDDIR", &numSounds);
}

/**************************************************************************
** loadAGIFile
**
** Purpose: To read an AGI data file out of a VOL file and store the data
** and data size into the AGIFile structure whose pointer is passed in.
**************************************************************************/
void loadAGIFile(AGIFilePosType location, AGIFile *AGIData)
{
   FILE *fp;
   short int sig;
   unsigned char byte1, byte2;

   if (location.filePos == EMPTY) {
      printf("Could not find requested AGI file.\n");
      printf("This could indicate problems with your game data files\n");
      printf("or there may be something wrong with MEKA.\n");
      exit(0);
   }

   if ((fp = fopen(location.fileName, "rb")) == NULL) {
      printf("Could not find file : %s.\n", location.fileName);
      printf("Make sure you are in an AGI version 2 game directory.\n");
      exit(0);
   }

   fseek(fp, location.filePos, SEEK_SET);
   fread(&sig, 2, 1, fp);
   if (sig != 0x3412) {  /* All AGI data files start with 0x1234 */
      printf("Data error reading %s.\n", location.fileName);
      printf("The requested AGI file did not have a signature.\n");
      printf("Check that if your game files are corrupt.\n");
      exit(0);
   }
   fgetc(fp); /* Ignore VOL file number. Not needed. */
   byte1 = fgetc(fp);
   byte2 = fgetc(fp);
   AGIData->size = (unsigned int)(byte1) + (unsigned int)(byte2 << 8);
   AGIData->data = (char *)malloc(AGIData->size);
   fread(AGIData->data, AGIData->size, 1, fp);

   fclose(fp);
}
