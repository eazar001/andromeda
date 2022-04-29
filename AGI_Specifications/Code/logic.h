/**************************************************************************
** LOGIC.H
**************************************************************************/

#ifndef _LOGIC_H_
#define _LOGIC_H_

char ENCRYPTED = 1;    /* Determines whether to use Avis Durgan
                          This will be changed to 0 for AGI version 3
                          games if we decide to support them. */

typedef struct {
   word codeSize;
   byte *logicCode;
   byte numMessages;
   byte **messages;
} LOGICFile;

void loadLogicFile(int logFileNum, LOGICFile *logicData);

#endif  /* _LOGIC_H_ */
