/**************************************************************************
** AGIFILES.H
**************************************************************************/

#ifndef _AGIFILES_H_
#define _AGIFILES_H_

typedef struct {          /* DIR entry structure */
   char *fileName;
   long filePos;
} AGIFilePosType;

typedef struct {          /* AGI data file structure */
   unsigned int size;
   char *data;
} AGIFile;

extern AGIFilePosType logdir[256], picdir[256], viewdir[256], snddir[256];
extern int numLogics, numPictures, numViews, numSounds;

void loadAGIDirs();
void loadAGIFile(AGIFilePosType location, AGIFile *AGIData);

#endif  /* _AGIFILES_H_ */
