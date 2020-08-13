'\nGenerate model to scale analog data to user defined range\nSource: http://code.activestate.com/recipes/578914-simple-linear-regression-with-pure-python/\n\nAuthor : Chaobin Tang  http://code.activestate.com/recipes/users/4174076/\nLicense : MIT\n\n'
import math
from ST7735 import TFT
from sysfont import sysfont
def mean(xs):return sum(xs)/len(xs)
def std(xs,m):A=len(xs)-1;return math.sqrt(sum((pow(A-m,2)for A in xs))/A)
def pearson_r(xs,ys,m_x,m_y):
	A=0;B=0;C=0
	for (F,G) in zip(xs,ys):D=F-m_x;E=G-m_y;A+=D*E;B+=pow(D,2);C+=pow(E,2)
	return A/math.sqrt(B*C)
def fit(x,y):
	'\n    Fit and generate model function\n    :param x: list\n    :param y:\n    :return:\n    ';A=mean(x);B=mean(y);D=pearson_r(x,y,A,B);C=D*(std(y,B)/std(x,A));E=B-C*A
	def F(_x):return C*_x+E
	return F
def boot_display(_tft):A=_tft;A.fillrect((0,0),(128,50),TFT.WHITE);A.fillrect((0,50),(128,160),TFT.GREEN);A.text((2,2),'BOOTING',TFT.BLACK,sysfont,1.1,nowrap=False)