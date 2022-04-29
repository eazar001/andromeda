/* C Header File: ADLIB *****************************************************

Author:		Kevin A. Lee

Last Amended:	27th April, 1993

Description:    Low-level interface to the Adlib (or compatible)
		FM sound card. All information gleaned from
		Jeffrey S. Lee's "Programming the Adlib/Sound
		Blaster FM Music Chips". See Lee's document for
		further information.

Compiled succesfully under Turbo C, Borland C++,
and Microsoft Quick C (all latest versions).

****************************************************************************/

#define MIN_REGISTER        0x01
#define MAX_REGISTER        0xF5
#define ADLIB_FM_ADDRESS    0x388       /* adlib address/status register */
#define ADLIB_FM_DATA       0x389       /* adlib data register           */

#ifndef BYTE
#define BYTE unsigned char
#endif


/*
* FM Instrument definition for .SBI files - SoundBlaster instrument
* - these are the important parts - we will skip the header, but since
*   I am not sure where it starts and ends so I have had to guess.
*   However it SEEMS! to work. Each array has two values, one for
*   each operator.
*/
typedef struct
{
   BYTE SoundCharacteristic[2];    /* modulator frequency multiple...  */
   BYTE Level[2];                  /* modulator frequency level...     */
   BYTE AttackDecay[2];            /* modulator attack/decay...        */
   BYTE SustainRelease[2];         /* modulator sustain/release...     */
   BYTE WaveSelect[2];             /* output waveform distortion       */
   BYTE Feedback;                  /* feedback algorithm and strength  */

} FMInstrument;


/*
* Enumerated F-Numbers (in octave 4) for the chromatic scale.
*/
enum SCALE
{
   D4b = 0x16B,    D4  = 0x181,    E4b = 0x198,    E4  = 0x1B0,
   F4  = 0x1CA,    G4b = 0x1E5,    G4  = 0x202,    A4b = 0x220,
   A4  = 0x241,    B4b = 0x263,    B4  = 0x287,    C4  = 0x2AE
};


/* function prototyping */
void WriteFM(int reg, int value);
int  ReadFM(void);
int  AdlibExists(void);
void FMReset(void);
void FMKeyOff(int voice);
void FMKeyOn(int voice, int freq, int octave);
void FMVoiceVolume(int voice, int vol);
void FMSetVoice(int voiceNum, FMInstrument *ins);
int  LoadSBI(char filename[], FMInstrument *ins);

