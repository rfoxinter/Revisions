from random import shuffle as sh
from subprocess import run as s
from subprocess import PIPE
from os import chdir as c
from os import remove as rem
from os import rename as ren
from os import makedirs as m
from os import listdir as l
from os.path import realpath,dirname
from os.path import dirname as d
from os.path import exists as e
from os.path import splitext as sp
from platform import system
from re import sub
import argparse

def b(a:str) -> bool:
    if 'True' in a:
        return True
    if 'False' in a:
        return False
    raise ValueError('La valuer n\u2019est pas un bouléen')

parser=argparse.ArgumentParser()
parser.add_argument('file',type=str)
parser.add_argument('--n',type=int,help='Number of flascards',default=1)
parser.add_argument('--dest',type=str,help='Destination folder',default='default')
parser.add_argument('--open',type=b,help='Open destination folder after generating pdfs',default='False')
args=parser.parse_args()

def remove_special_chars(string:str) -> str:
    string=sub(u'[ ]','',string)
    string=sub(u'[àáâä]','a',string)
    string=sub(u'[èéêë]','e',string)
    string=sub(u'[îï]','i',string)
    string=sub(u'[ôö]','o',string)
    string=sub(u'[ùúûü]','u',string)
    string=sub(u'[ç]','c',string)
    string=sub(u'[ÀÁÂÄ]','A',string)
    string=sub(u'[ÈÉÊË]','E',string)
    string=sub(u'[ÎÏ]','I',string)
    string=sub(u'[ÔÖ]','O',string)
    string=sub(u'[ÙÚÛÜ]','U',string)
    string=sub(u'[Ç]','C',string)
    return string

def output_f(files:list) -> list:
    ret = []
    for i in files:
        r = open(i, 'r').read()
        st = r.find('{pdftitle=')
        k = st + 11
        while r[k] != '}':
            k += 1
        t = r[st + 10:k]
        dest = t.split('--')
        if len(dest) == 1:
            dest = 'pdf/'
        else:
            dest = 'pdf/'+remove_special_chars(dest[0].title())+'/'
        ret.append(dest)
    return ret

def recompile(dest:str) -> bool:
    fail = False
    c(d(__file__))
    c(d('output/'))
    files = [i for i in sorted(l('.')) if sp(i)[1]=='.tex']
    output = [dest for i in files] if dest != 'default' else output_f(files)
    for i in range(len(files)):
        c(d(__file__))
        c(d('output/'))
        ttle = files[i].replace('.tex','')
        dest = output[i]
        print('Compilation en cours [' + str(i+1) + '/' + str(len(files)) + ']\nCompilation de [' + files[i] + ']\n')
        out = s('latexmk -synctex=1 -interaction=nonstopmode -file-line-error -pdf '+ ttle, shell = True, stdout = PIPE, stderr = PIPE, text=True).stdout
        if 'Command for \'pdflatex\' gave return code 1' in out:
            print(out + '\n')
            fail = True
        if e('../' + ttle + '.pdf'):
            rem('../' + ttle + '.pdf')
        ext = ['.aux','.fdb_latexmk','.fdb_latexmk','.fls','.log','.nav','.out','.snm','.synctex.gz','.toc']
        for i in ext:
            try:
                rem(ttle + i)
            except OSError:
                pass
        c('../')
        if not e(dest):
            try:
                m(dest)
            except OSError:
                fail = True
        try:
            ren('output/' + ttle + '.pdf', dest + ttle + '.pdf')
        except:
            fail = True
    return fail

def gen_latex(r:list,t:str,ttle:str,dest:str) -> bool:
    c(d(__file__))
    sh_quest,sh_qr,defs=b(r[1]),b(r[2]),r[3]
    r = [r[i].split(';;') for i in range(4,len(r))]
    if sh_qr:
        for i in r:
            sh(i)
    if sh_quest:
        sh(r)
    del sh_qr,sh_quest
    t2 = t.split(' -- ')
    if len(t2)==1:
        t2 = t2[0]
    else:
        t2 = t2[0] + '\\\\\\emph{' + t2[1] + '}'
    file = '''\\documentclass[14pt,usepdftitle=false,aspectratio=169]{beamer}
\\usepackage{preambule}
\\setbeamercolor{structure}{fg=black}
''' + defs + '''
\\hypersetup{pdftitle=''' + t + '''}
\\title{''' + t2 + '''}
\\author{}
\\date{}
\\begin{document}
\\begin{frame}
    \\titlepage
\\end{frame}
'''
    del defs,t2
    for i in range(len(r)):
        if r[i][0][0:5]=='!!fst':
            r[i][0] = r[i][0].replace('!!fst','')
        elif r[i][1][0:5]=='!!fst':
            r[i][0],r[i][1] = r[i][1].replace('!!fst',''),r[i][0]
        file += '\\slideq{' + r[i][0] + '}{' + str(i+1) + '/' + str(len(r)) + '}\n'
        file += '\\slider{' + r[i][1] + '}{' + str(i+1) + '/' + str(len(r)) + '}\n'
    file += '\end{document}'
    f = open('output/' + ttle + '.tex','w')
    f.write(file)
    f.close()
    c('output/')
    fail = False
    print('Compilation en cours\n')
    output = s('latexmk -synctex=1 -interaction=nonstopmode -file-line-error -pdf '+ ttle, shell = True, stdout = PIPE, stderr = PIPE, text=True).stdout
    if 'Command for \'pdflatex\' gave return code 1' in output:
        print(output + '\n')
        fail = True
    if e('../' + ttle + '.pdf'):
        rem('../' + ttle + '.pdf')
    ext = ['.aux','.fdb_latexmk','.fdb_latexmk','.fls','.log','.nav','.out','.snm','.synctex.gz','.toc']
    for i in ext:
        try:
            rem(ttle + i)
        except OSError:
            pass
    c('../')
    if not e(dest):
        try:
            m(dest)
        except OSError:
            fail = True
    try:
        ren('output/' + ttle + '.pdf', dest + ttle + '.pdf')
    except:
        fail = True
    return fail

def main(file_path:str,file:str,n:int,dest:str,_open:bool) -> bool:
    fail = False
    if file == '__recompile__':
        return recompile(dest)
    c(dirname(realpath(file_path)))
    if file == '':
        file = input('Chapitre : ').split(';;')
    try:
        r = open('input/'+file+'.txt', 'r').read().split('\n')
    except OSError:
        raise RuntimeError('Fichier introuvable')
    t, ttle = '', ''
    if '!ttle' in r[0]:
        ttle, t = r[0].split('!!ttle')
    else:
        t = r[0]
        ttle = t.split('--')
        if len(ttle) == 1:
            ttle = ttle[0].title()
        else:
            ttle = ttle[1].title()
        ttle = remove_special_chars(ttle)
    if dest == 'default':
        dest = t.split('--')
        if len(dest) == 1:
            dest = 'pdf/'
        else:
            dest = 'pdf/'+remove_special_chars(dest[0].title())+'/'
    if n == 1:
        fail = gen_latex(r,t,ttle,dest)
    else:
        for j in range(n):
            fail = gen_latex(r,t,ttle+'.'+str(j+1),dest) and fail
    if _open:
        if system() == 'Windows':
            if s('start ' + dest, shell = True, stdout = PIPE, stderr = PIPE, text=True).stdout != '':
                print('Impossible d\u2019ouvrir le dossier\n')
        else:
            if s('open ' + dest, shell = True, stdout = PIPE, stderr = PIPE, text=True).stdout != '':
                print('Impossible d\u2019ouvrir le dossier\n')
    return fail

if __name__=='__main__':
    if main(__file__,args.file,args.n,args.dest,args.open):
        raise RuntimeError('Une erreur est survenue')
    print('Compilation terminée')