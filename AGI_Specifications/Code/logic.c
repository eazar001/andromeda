/**************************************************************************
** LOGIC.C
**
** These functions are used to load LOGIC files into a structure of type
** LOGICFile. It uses the general function LoadAGIFile to load the data
** from the VOL file itself.
**
** (c) 1997 Lance Ewing - Original code (2 July 97)
**************************************************************************/

#include <string.h>

#include "agifiles.h"
#include "general.h"
#include "logic.h"

#define  AVIS_DURGAN  "Avis Durgan"

/**************************************************************************
** loadMessages
**
** Purpose: To unencrypt the message section of the LOGIC file and store
** in the message array which is part of the LOGICFile struct.
**************************************************************************/
void loadMessages(byte *fileData, LOGICFile *logicData)
{
   word startPos, endPos, i, messNum, avisPos;
   short int index;
   byte *marker;

   /* Calculate start and end indices of message data, and
   ** the number of messages in message data, and then allocate
   ** memory for the array of message strings. */
   startPos = fileData[0] + fileData[1]*256 + 2;
   endPos = fileData[startPos+1] + fileData[startPos+2]*256;
   logicData->numMessages = fileData[startPos];
   logicData->messages = (byte **)malloc(logicData->numMessages*sizeof(byte *));

   /* Unencrypt the message data with the "Avis Durgan" string. */
   fileData += (startPos + 3);
   if (ENCRYPTED)
      for (i=(logicData->numMessages*2), avisPos=0; i<endPos; i++, avisPos++)
	      fileData[i] ^= AVIS_DURGAN[avisPos % 11];

   /* Step through the message data copying message strings to the
   ** logicData struct. */
   for (messNum=0, marker=fileData; messNum<logicData->numMessages; messNum++, marker+=2) {
      index = marker[0] + marker[1]*256 - 2;
      logicData->messages[messNum] = ((index<0)? strdup("")
         : strdup(&fileData[index]));
   }
}

/**************************************************************************
** loadLogicFile
**
** Purpose: To load a LOGIC file, decode the messages, and store in a
** suitable structure.
**************************************************************************/
void loadLogicFile(int logFileNum, LOGICFile *logicData)
{
   AGIFile tempAGI;

   /* Load LOGIC file, calculate logic code length, and copy
   ** logic code into tempLOGIC. */
   loadAGIFile(logdir[logFileNum], &tempAGI);
   logicData->codeSize = tempAGI.data[0] + tempAGI.data[1]*256;
   logicData->logicCode = (byte *)malloc(logicData->codeSize);
   memcpy(logicData->logicCode, &tempAGI.data[2], logicData->codeSize);

   /* Decode message section of LOGIC file and store in tempLOGIC. */
   loadMessages(tempAGI.data, logicData);

   free(tempAGI.data);   /* Deallocate original buffer. */
}

/**************************************************************************
** discardLogicFile
**
** Purpose: To deallocate all the memory associated with a LOGICFile
** struct. This function can only be used with dynamically allocated
** LOGICFile structs which is what I plan to use. The LOGICs loaded
** into memory will be contained in a linked list.
**************************************************************************/
void discardLogicFile(LOGICFile *logicData)
{
   int messNum;

   for (messNum=0; messNum<logicData->numMessages; messNum++)
      free(logicData->messages[messNum]);

   free(logicData->messages);
   free(logicData->logicCode);
   free(logicData);
}

void testLoad()
{
   LOGICFile *test;

   loadAGIDirs();
   test = (LOGICFile *)malloc(sizeof(LOGICFile));
   loadLogicFile(0, test);
   discardLogicFile(test);
}
