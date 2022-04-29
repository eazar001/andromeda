program GetAGIVersionNumber;

(*by Jeremy W. Hayes a.k.a. 'Version Control'                         *)
(*http://www.concentric.net/~mikeph/index.html (Avis Durgan)          *)
(*mikeph@concentric.net                                               *)
(*03-16-97                                                            *)

(*This does the job of picking out the version number from AGIData.Ovl*)
(*I allow anybody to use this code, and in fact want them to do so,   *)
(*So we have less gliches of sorts, from slight structure differences.*)

(*Now you know the REAL reason behind version control, because I knew *)
(*that we would run into this little problem sooner or later, and I'm *)
(*ready, with plenty of information and data.                         *)

uses DOS;

const 
  InFileName='agidata.ovl';

type
  VersionNumType=string[9];

var
  VersionNumBuffer:VersionNumType;
  ByteBuffer:Byte;
  InFile:File of Byte;
  ISVerNum:Boolean;
  X:Integer;
  VerLen:Byte;

begin
  VersionNumBuffer:='A_CDE_GHI';
  assign(InFile,InFileName);
  reset(InFile);
  while not EOF(InFile) do
    begin
      Read(InFile,ByteBuffer);
      VersionNumBuffer:=Concat(copy (VersionNumBuffer,2,8),Chr(ByteBuffer));
      VerLen:=0;
      ISVerNum:=TRUE;
      If VersionNumBuffer[2]='.'
        then
          begin
            If (VersionNumBuffer[1]<'0') or (VersionNumBuffer[1]>'9')
              then ISVerNum:=FALSE;
            For X:=3 to 5 do
              IF (VersionNumBuffer[X]<'0') or (VersionNumBuffer[X]>'9')
                then ISVerNum:=FALSE;
            If (ISVerNum) and (VersionNumBuffer[1]<='2')
              then VerLen:=5;
            If VersionNumBuffer[6]<>'.'
              then ISVerNum:=FALSE;
            For X:=7 to 9 do
              IF (VersionNumBuffer[X]<'0') or (VersionNumBuffer[X]>'9')
                then ISVerNum:=FALSE;
            If ISVerNum
              then VerLen:=9;
          end
        else ISVerNum:=FALSE;
      If VerLen>0
        then
          begin
            for X:=1 to VerLen do
              Write(VersionNumBuffer[X]);
            WriteLn;
          end;
    end;
  close(InFile);
end.
