'\ndriver for Sainsmart 1.8" TFT display ST7735\nTranslated by Guy Carver from the ST7735 sample code.\nModified for micropython-esp32 by boochow\n\nsource : https://github.com/boochow/MicroPython-ST7735\nAuthor : boochow @github\n\nPins connection\nLCD (Yourbot)    ESP32\n==============================\nVLED/BLK         3V3\nRST \t         IO17\nA0/DC/RS         IO16(DC)\nSDA              IO13(MOSI)\nSCK              IO14(CLK)\nVCC              3V3\nCS \t             IO18\nGND              GND\n\n\nLCD (Az Delevery)    ESP32\n==============================\nVLED/BLK         3V3\nRST \t         IO4\nA0/DC/RS         IO2\nSDA              IO23\nSCK              IO18\nVCC              5v\nCS \t             IO15\nGND              GND\n\n\n\n'
_F='Height'
_E='Width'
_D='Initializing'
_C='X2'
_B='X1'
_A=True
import machine,time
from math import sqrt
TFTRotations=[0,96,192,160]
TFTBGR=8
TFTRGB=0
def clamp(aValue,aMin,aMax):return max(aMin,min(aMax,aValue))
def TFTColor(aR,aG,aB):'Create a 16 bit rgb value from the given R,G,B from 0-255.\n       This assumes rgb 565 layout and will be incorrect for bgr.';return(aR&248)<<8|(aG&252)<<3|aB>>3
ScreenSize=128,160
class TFT:
	'Sainsmart TFT 7735 display driver.';NOP=0;SWRESET=1;RDDID=4;RDDST=9;SLPIN=16;SLPOUT=17;PTLON=18;NORON=19;INVOFF=32;INVON=33;DISPOFF=40;DISPON=41;CASET=42;RASET=43;RAMWR=44;RAMRD=46;VSCRDEF=51;VSCSAD=55;COLMOD=58;MADCTL=54;FRMCTR1=177;FRMCTR2=178;FRMCTR3=179;INVCTR=180;DISSET5=182;PWCTR1=192;PWCTR2=193;PWCTR3=194;PWCTR4=195;PWCTR5=196;VMCTR1=197;RDID1=218;RDID2=219;RDID3=220;RDID4=221;PWCTR6=252;GMCTRP1=224;GMCTRN1=225;BLACK=0;RED=TFTColor(255,0,0);MAROON=TFTColor(128,0,0);GREEN=TFTColor(0,255,0);FOREST=TFTColor(0,128,128);BLUE=TFTColor(0,0,255);NAVY=TFTColor(0,0,128);CYAN=TFTColor(0,255,255);YELLOW=TFTColor(255,255,0);PURPLE=TFTColor(255,0,255);WHITE=TFTColor(255,255,255);GRAY=TFTColor(128,128,128)
	@staticmethod
	def color(aR,aG,aB):'Create a 565 rgb TFTColor value';return TFTColor(aR,aG,aB)
	def __init__(A,spi,aDC,aReset,aCS):"aLoc SPI pin location is either 1 for 'X' or 2 for 'Y'.\n           aDC is the DC pin and aReset is the reset pin.";A._size=ScreenSize;A._offset=bytearray([0,0]);A.rotate=0;A._rgb=_A;A.tfa=0;A.bfa=0;A.dc=machine.Pin(aDC,machine.Pin.OUT,machine.Pin.PULL_DOWN);A.reset=machine.Pin(aReset,machine.Pin.OUT,machine.Pin.PULL_DOWN);A.cs=machine.Pin(aCS,machine.Pin.OUT,machine.Pin.PULL_DOWN);A.cs(1);A.spi=spi;A.colorData=bytearray(2);A.windowLocData=bytearray(4)
	def size(A):return A._size
	def on(A,aTF=_A):'Turn display on or off.';A._writecommand(TFT.DISPON if aTF else TFT.DISPOFF)
	def invertcolor(A,aBool):'Invert the color data IE: Black = White.';A._writecommand(TFT.INVON if aBool else TFT.INVOFF)
	def rgb(A,aTF=_A):'True = rgb else bgr';A._rgb=aTF;A._setMADCTL()
	def rotation(A,aRot):
		'0 - 3. Starts vertical with top toward pins and rotates 90 deg\n           clockwise each step.';B=aRot
		if 0<=B<4:
			C=A.rotate^B;A.rotate=B
			if C&1:A._size=A._size[1],A._size[0]
			A._setMADCTL()
	def pixel(A,aPos,aColor):
		'Draw a pixel at the given position';B=aPos
		if 0<=B[0]<A._size[0]and 0<=B[1]<A._size[1]:A._setwindowpoint(B);A._pushcolor(aColor)
	def text(E,aPos,aString,aColor,aFont,aSize=1,nowrap=False):
		'Draw a text at the given position.  If the string reaches the end of the\n           display it is wrapped to aPos[0] on the next line.  aSize may be an integer\n           which will size the font uniformly on w,h or a or any type that may be\n           indexed with [0] or [1].';B=aFont;A=aSize
		if B==None:return
		if type(A)==int or type(A)==float:C=A,A
		else:C=A
		D,F=aPos;G=C[0]*B[_E]+1
		for H in aString:
			E.char((D,F),H,aColor,B,C);D+=G
			if D+G>E._size[0]:
				if nowrap:break
				else:F+=B[_F]*C[1]+1;D=aPos[0]
	def char(J,aPos,aChar,aColor,aFont,aSizes):
		'Draw a character at the given position using the given font and color.\n           aSizes is a tuple with x, y as integer scales indicating the\n           # of pixels to draw for each pixel in the character.';H=aColor;D=aSizes;B=aFont;A=aPos
		if B==None:return
		K=B['Start'];R=B['End'];E=ord(aChar)
		if K<=E<=R:
			C=B[_E];G=B[_F];E=(E-K)*C;L=B['Data'][E:E+C];M=A[0]
			if D[0]<=1 and D[1]<=1:
				I=bytearray(2*G*C)
				for N in range(C):
					F=L[N]
					for O in range(G):
						if F&1:P=2*(O*C+N);I[P]=H>>8;I[P+1]=H&255
						F>>=1
				J.image(A[0],A[1],A[0]+C-1,A[1]+G-1,I)
			else:
				for F in L:
					Q=A[1]
					for O in range(G):
						if F&1:J.fillrect((M,Q),D,H)
						Q+=D[1];F>>=1
					M+=D[0]
	def line(H,aStart,aEnd,aColor):
		'Draws a line from aStart to aEnd in the given color.  Vertical or horizontal\n           lines are forwarded to vline and hline.';I=aColor;D=aEnd;C=aStart
		if C[0]==D[0]:J=D if D[1]<C[1]else C;H.vline(J,abs(D[1]-C[1])+1,I)
		elif C[1]==D[1]:J=D if D[0]<C[0]else C;H.hline(J,abs(D[0]-C[0])+1,I)
		else:
			F,G=C;K,L=D;A=K-F;B=L-G;M=1 if A>0 else-1;N=1 if B>0 else-1;A=abs(A);B=abs(B)
			if A>=B:
				B<<=1;E=B-A;A<<=1
				while F!=K:
					H.pixel((F,G),I)
					if E>=0:G+=N;E-=A
					E+=B;F+=M
			else:
				A<<=1;E=A-B;B<<=1
				while G!=L:
					H.pixel((F,G),I)
					if E>=0:F+=M;E-=B
					E+=A;G+=N
	def vline(A,aStart,aLen,aColor):
		'Draw a vertical line from aStart for aLen. aLen may be negative.';D=aStart;B=clamp(D[0],0,A._size[0]),clamp(D[1],0,A._size[1]);C=B[0],clamp(B[1]+aLen,0,A._size[1])
		if C[1]<B[1]:B,C=C,B
		A._setwindowloc(B,C);A._setColor(aColor);A._draw(aLen)
	def hline(A,aStart,aLen,aColor):
		'Draw a horizontal line from aStart for aLen. aLen may be negative.';D=aStart;B=clamp(D[0],0,A._size[0]),clamp(D[1],0,A._size[1]);C=clamp(B[0]+aLen,0,A._size[0]),B[1]
		if C[0]<B[0]:B,C=C,B
		A._setwindowloc(B,C);A._setColor(aColor);A._draw(aLen)
	def rect(C,aStart,aSize,aColor):'Draw a hollow rectangle.  aStart is the smallest coordinate corner\n           and aSize is a tuple indicating width, height.';D=aColor;B=aSize;A=aStart;C.hline(A,B[0],D);C.hline((A[0],A[1]+B[1]-1),B[0],D);C.vline(A,B[1],D);C.vline((A[0]+B[0]-1,A[1]),B[1],D)
	def fillrect(C,aStart,aSize,aColor):
		'Draw a filled rectangle.  aStart is the smallest coordinate corner\n           and aSize is a tuple indicating width, height.';F=aSize;E=aStart;A=clamp(E[0],0,C._size[0]),clamp(E[1],0,C._size[1]);B=clamp(A[0]+F[0]-1,0,C._size[0]),clamp(A[1]+F[1]-1,0,C._size[1])
		if B[0]<A[0]:D=B[0];B=A[0],B[1];A=D,A[1]
		if B[1]<A[1]:D=B[1];B=B[0],A[1];A=A[0],D
		C._setwindowloc(A,B);G=(B[0]-A[0]+1)*(B[1]-A[1]+1);C._setColor(aColor);C._draw(G)
	def circle(A,aPos,aRadius,aColor):
		'Draw a hollow circle with the given radius and color with aPos as center.';F=aColor;E=aRadius;B=aPos;A.colorData[0]=F>>8;A.colorData[1]=F;O=int(0.7071*E)+1;P=E*E
		for C in range(O):D=int(sqrt(P-C*C));G=B[0]+C;H=B[1]+D;I=B[0]-C;J=B[1]-D;K=B[0]+D;L=B[1]+C;M=B[0]-D;N=B[1]-C;A._setwindowpoint((G,H));A._writedata(A.colorData);A._setwindowpoint((G,J));A._writedata(A.colorData);A._setwindowpoint((I,H));A._writedata(A.colorData);A._setwindowpoint((I,J));A._writedata(A.colorData);A._setwindowpoint((K,L));A._writedata(A.colorData);A._setwindowpoint((K,N));A._writedata(A.colorData);A._setwindowpoint((M,L));A._writedata(A.colorData);A._setwindowpoint((M,N));A._writedata(A.colorData)
	def fillcircle(C,aPos,aRadius,aColor):
		'Draw a filled circle with given radius and color with aPos as center';F=aColor;E=aRadius;D=aPos;I=E*E
		for B in range(E):G=int(sqrt(I-B*B));A=D[1]-G;J=A+G*2;A=clamp(A,0,C._size[1]);H=abs(J-A)+1;C.vline((D[0]+B,A),H,F);C.vline((D[0]-B,A),H,F)
	def fill(A,aColor=BLACK):'Fill screen with the given color.';A.fillrect((0,0),A._size,aColor)
	def image(A,x0,y0,x1,y1,data):A._setwindowloc((x0,y0),(x1,y1));A._writedata(data)
	def setvscroll(A,tfa,bfa):' set vertical scroll area ';D=bfa;C=tfa;A._writecommand(TFT.VSCRDEF);B=bytearray([0,C]);A._writedata(B);B[1]=162-C-D;A._writedata(B);B[1]=D;A._writedata(B);A.tfa=C;A.bfa=D
	def vscroll(A,value):
		B=value+A.tfa
		if B+A.bfa>162:B=162-A.bfa
		A._vscrolladdr(B)
	def _vscrolladdr(A,addr):A._writecommand(TFT.VSCSAD);B=bytearray([addr>>8,addr&255]);A._writedata(B)
	def _setColor(A,aColor):B=aColor;A.colorData[0]=B>>8;A.colorData[1]=B;A.buf=bytes(A.colorData)*32
	def _draw(A,aPixels):
		'Send given color to the device aPixels times.';B=aPixels;A.dc(1);A.cs(0)
		for E in range(B//32):A.spi.write(A.buf)
		C=int(B)%32
		if C>0:D=bytes(A.colorData)*C;A.spi.write(D)
		A.cs(1)
	def _setwindowpoint(A,aPos):'Set a single point for drawing a color to.';B=A._offset[0]+int(aPos[0]);C=A._offset[1]+int(aPos[1]);A._writecommand(TFT.CASET);A.windowLocData[0]=A._offset[0];A.windowLocData[1]=B;A.windowLocData[2]=A._offset[0];A.windowLocData[3]=B;A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[0]=A._offset[1];A.windowLocData[1]=C;A.windowLocData[2]=A._offset[1];A.windowLocData[3]=C;A._writedata(A.windowLocData);A._writecommand(TFT.RAMWR)
	def _setwindowloc(A,aPos0,aPos1):'Set a rectangular area for drawing a color to.';C=aPos1;B=aPos0;A._writecommand(TFT.CASET);A.windowLocData[0]=A._offset[0];A.windowLocData[1]=A._offset[0]+int(B[0]);A.windowLocData[2]=A._offset[0];A.windowLocData[3]=A._offset[0]+int(C[0]);A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[0]=A._offset[1];A.windowLocData[1]=A._offset[1]+int(B[1]);A.windowLocData[2]=A._offset[1];A.windowLocData[3]=A._offset[1]+int(C[1]);A._writedata(A.windowLocData);A._writecommand(TFT.RAMWR)
	def _writecommand(A,aCommand):'Write given command to the device.';A.dc(0);A.cs(0);A.spi.write(bytearray([aCommand]));A.cs(1)
	def _writedata(A,aData):'Write given data to the device.  This may be\n           either a single int or a bytearray of values.';A.dc(1);A.cs(0);A.spi.write(aData);A.cs(1)
	def _pushcolor(A,aColor):'Push given color to the device.';B=aColor;A.colorData[0]=B>>8;A.colorData[1]=B;A._writedata(A.colorData)
	def _setMADCTL(A):'Set screen rotation and RGB/BGR format.';A._writecommand(TFT.MADCTL);B=TFTRGB if A._rgb else TFTBGR;A._writedata(bytearray([TFTRotations[A.rotate]|B]))
	def _reset(A):'Reset the device.';A.dc(0);A.reset(1);time.sleep_us(500);A.reset(0);time.sleep_us(500);A.reset(1);time.sleep_us(500)
	def initb(A):'Initialize blue tab version.';A._size=ScreenSize[0]+2,ScreenSize[1]+1;A._reset();A._writecommand(TFT.SWRESET);time.sleep_us(50);A._writecommand(TFT.SLPOUT);time.sleep_us(500);C=bytearray(1);A._writecommand(TFT.COLMOD);C[0]=5;A._writedata(C);time.sleep_us(10);D=bytearray([0,6,3]);A._writecommand(TFT.FRMCTR1);A._writedata(D);time.sleep_us(10);A._writecommand(TFT.MADCTL);C[0]=8;A._writedata(C);B=bytearray(2);A._writecommand(TFT.DISSET5);B[0]=21;B[1]=2;A._writedata(B);A._writecommand(TFT.INVCTR);C[0]=0;A._writedata(C);A._writecommand(TFT.PWCTR1);B[0]=2;B[1]=112;A._writedata(B);time.sleep_us(10);A._writecommand(TFT.PWCTR2);C[0]=5;A._writedata(C);A._writecommand(TFT.PWCTR3);B[0]=1;B[1]=2;A._writedata(B);A._writecommand(TFT.VMCTR1);B[0]=60;B[1]=56;A._writedata(B);time.sleep_us(10);A._writecommand(TFT.PWCTR6);B[0]=17;B[1]=21;A._writedata(B);E=bytearray([2,28,7,18,55,50,41,45,41,37,43,57,0,1,3,16]);A._writecommand(TFT.GMCTRP1);A._writedata(E);F=bytearray([3,29,7,6,46,44,41,45,46,46,55,63,0,0,2,16]);A._writecommand(TFT.GMCTRN1);A._writedata(F);time.sleep_us(10);A._writecommand(TFT.CASET);A.windowLocData[0]=0;A.windowLocData[1]=2;A.windowLocData[2]=0;A.windowLocData[3]=A._size[0]-1;A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[1]=1;A.windowLocData[3]=A._size[1]-1;A._writedata(A.windowLocData);A._writecommand(TFT.NORON);time.sleep_us(10);A._writecommand(TFT.RAMWR);time.sleep_us(500);A._writecommand(TFT.DISPON);A.cs(1);time.sleep_us(500)
	def initr(A):'Initialize a red tab version.';A._reset();A._writecommand(TFT.SWRESET);time.sleep_us(150);A._writecommand(TFT.SLPOUT);time.sleep_us(500);D=bytearray([1,44,45]);A._writecommand(TFT.FRMCTR1);A._writedata(D);A._writecommand(TFT.FRMCTR2);A._writedata(D);E=bytearray([1,44,45,1,44,45]);A._writecommand(TFT.FRMCTR3);A._writedata(E);time.sleep_us(10);B=bytearray(1);A._writecommand(TFT.INVCTR);B[0]=7;A._writedata(B);A._writecommand(TFT.PWCTR1);D[0]=162;D[1]=2;D[2]=132;A._writedata(D);A._writecommand(TFT.PWCTR2);B[0]=197;A._writedata(B);C=bytearray(2);A._writecommand(TFT.PWCTR3);C[0]=10;C[1]=0;A._writedata(C);A._writecommand(TFT.PWCTR4);C[0]=138;C[1]=42;A._writedata(C);A._writecommand(TFT.PWCTR5);C[0]=138;C[1]=238;A._writedata(C);A._writecommand(TFT.VMCTR1);B[0]=14;A._writedata(B);A._writecommand(TFT.INVOFF);A._writecommand(TFT.MADCTL);B[0]=200;A._writedata(B);A._writecommand(TFT.COLMOD);B[0]=5;A._writedata(B);A._writecommand(TFT.CASET);A.windowLocData[0]=0;A.windowLocData[1]=0;A.windowLocData[2]=0;A.windowLocData[3]=A._size[0]-1;A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[3]=A._size[1]-1;A._writedata(A.windowLocData);F=bytearray([15,26,15,24,47,40,32,34,31,27,35,55,0,7,2,16]);A._writecommand(TFT.GMCTRP1);A._writedata(F);G=bytearray([15,27,15,23,51,44,41,46,48,48,57,63,0,7,3,16]);A._writecommand(TFT.GMCTRN1);A._writedata(G);time.sleep_us(10);A._writecommand(TFT.DISPON);time.sleep_us(100);A._writecommand(TFT.NORON);time.sleep_us(10);A.cs(1)
	def initb2(A):'Initialize another blue tab version.';A._size=ScreenSize[0]+2,ScreenSize[1]+1;A._offset[0]=2;A._offset[1]=1;A._reset();A._writecommand(TFT.SWRESET);time.sleep_us(50);A._writecommand(TFT.SLPOUT);time.sleep_us(500);D=bytearray([1,44,45]);A._writecommand(TFT.FRMCTR1);A._writedata(D);time.sleep_us(10);A._writecommand(TFT.FRMCTR2);A._writedata(D);time.sleep_us(10);A._writecommand(TFT.FRMCTR3);A._writedata(D);time.sleep_us(10);A._writecommand(TFT.INVCTR);B=bytearray(1);B[0]=7;A._writedata(B);A._writecommand(TFT.PWCTR1);D[0]=162;D[1]=2;D[2]=132;A._writedata(D);time.sleep_us(10);A._writecommand(TFT.PWCTR2);B[0]=197;A._writedata(B);A._writecommand(TFT.PWCTR3);C=bytearray(2);C[0]=10;C[1]=0;A._writedata(C);A._writecommand(TFT.PWCTR4);C[0]=138;C[1]=42;A._writedata(C);A._writecommand(TFT.PWCTR5);C[0]=138;C[1]=238;A._writedata(C);A._writecommand(TFT.VMCTR1);B[0]=14;A._writedata(B);time.sleep_us(10);A._writecommand(TFT.MADCTL);B[0]=200;A._writedata(B);E=bytearray([2,28,7,18,55,50,41,45,41,37,43,57,0,1,3,16]);A._writecommand(TFT.GMCTRP1);A._writedata(E);F=bytearray([3,29,7,6,46,44,41,45,46,46,55,63,0,0,2,16]);A._writecommand(TFT.GMCTRN1);A._writedata(F);time.sleep_us(10);A._writecommand(TFT.CASET);A.windowLocData[0]=0;A.windowLocData[1]=2;A.windowLocData[2]=0;A.windowLocData[3]=A._size[0]-1;A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[1]=1;A.windowLocData[3]=A._size[1]-1;A._writedata(A.windowLocData);B=bytearray(1);A._writecommand(TFT.COLMOD);B[0]=5;A._writedata(B);time.sleep_us(10);A._writecommand(TFT.NORON);time.sleep_us(10);A._writecommand(TFT.RAMWR);time.sleep_us(500);A._writecommand(TFT.DISPON);A.cs(1);time.sleep_us(500)
	def initg(A):'Initialize a green tab version.';A._reset();A._writecommand(TFT.SWRESET);time.sleep_us(150);A._writecommand(TFT.SLPOUT);time.sleep_us(255);C=bytearray([1,44,45]);A._writecommand(TFT.FRMCTR1);A._writedata(C);A._writecommand(TFT.FRMCTR2);A._writedata(C);D=bytearray([1,44,45,1,44,45]);A._writecommand(TFT.FRMCTR3);A._writedata(D);time.sleep_us(10);A._writecommand(TFT.INVCTR);A._writedata(bytearray([7]));A._writecommand(TFT.PWCTR1);C[0]=162;C[1]=2;C[2]=132;A._writedata(C);A._writecommand(TFT.PWCTR2);A._writedata(bytearray([197]));B=bytearray(2);A._writecommand(TFT.PWCTR3);B[0]=10;B[1]=0;A._writedata(B);A._writecommand(TFT.PWCTR4);B[0]=138;B[1]=42;A._writedata(B);A._writecommand(TFT.PWCTR5);B[0]=138;B[1]=238;A._writedata(B);A._writecommand(TFT.VMCTR1);A._writedata(bytearray([14]));A._writecommand(TFT.INVOFF);A._setMADCTL();A._writecommand(TFT.COLMOD);A._writedata(bytearray([5]));A._writecommand(TFT.CASET);A.windowLocData[0]=0;A.windowLocData[1]=1;A.windowLocData[2]=0;A.windowLocData[3]=A._size[0]-1;A._writedata(A.windowLocData);A._writecommand(TFT.RASET);A.windowLocData[3]=A._size[1]-1;A._writedata(A.windowLocData);E=bytearray([2,28,7,18,55,50,41,45,41,37,43,57,0,1,3,16]);A._writecommand(TFT.GMCTRP1);A._writedata(E);F=bytearray([3,29,7,6,46,44,41,45,46,46,55,63,0,0,2,16]);A._writecommand(TFT.GMCTRN1);A._writedata(F);A._writecommand(TFT.NORON);time.sleep_us(10);A._writecommand(TFT.DISPON);time.sleep_us(100);A.cs(1)
def maker():A=TFT(1,_B,_C);print(_D);A.initr();A.fill(0);return A
def makeb():A=TFT(1,_B,_C);print(_D);A.initb();A.fill(0);return A
def makeg():A=TFT(1,_B,_C);print(_D);A.initg();A.fill(0);return A