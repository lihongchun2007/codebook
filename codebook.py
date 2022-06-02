import os
import shutil
import argparse
from pathlib import Path
from glob import glob

ext_lang_map = {
    '.rs':'rust',
    '.h':'c',
    '.c':'c',
    '.cpp':'cpp',
    '.hpp':'cpp',
    '.py':'python',
    '.js':'javascript',
    '.rb':'ruby',
    '.java':'java',
}

def getSourceFiles(root):
    path = os.path.join(root, '**')
    files = glob(path, recursive=True)
    source_files = list([fn for fn in files if isTextFile(fn)])
    source_files.sort()
    return source_files

def convertSource2Md(file_name, root, dest):
    with open(file_name, 'r', encoding='ascii', errors='ignore') as f:
        src_texts = f.readlines()
    short_name = removeRoot(file_name, root)
    short_name_noext, ext = os.path.splitext(short_name)
    lang = getCodeLanguage(ext)
    
    if not file_name.endswith('.md'):
        src_texts.insert(0, '\n# {}\n'.format(short_name))
        src_texts.insert(1, '```{}\n'.format(lang))
        src_texts.append('```\n')

    dest = Path(dest)
    dst_name = dest.joinpath(short_name_noext + '.md')
    dst_path = os.path.dirname(dst_name)
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    with open(dst_name, 'w', encoding='ascii', errors='ignore') as f:
        print('WRITE:', dest, short_name_noext, dst_name)
        f.writelines(src_texts)
    
    return short_name, dst_name.as_posix()


def getCodeLanguage(ext):
    global ext_lang_map
    try:
        return ext_lang_map[ext.lower()]
    except:
        return ''

def isTextFile(file_name):
    # if not os.path.isfile(file_name):
    #     return False
    try:
        with open(file_name, 'r', encoding='utf8') as f:
            f.readline()
            return True
    except:
        print('IGNORE:', file_name)
        return False

def removeRoot(path, root):
    path = Path(path).as_posix()
    root = Path(root).as_posix() + '/'
    return path.replace(root, '')

def main(root, dst):
    files = getSourceFiles(root)
    src_names, out_files =[], []
    for fn in files:
        src_fn, out_fn = convertSource2Md(fn, root, dst)
        src_names.append(src_fn)
        out_files.append(out_fn)

    dst = Path(dst)
    meta_file = 'meta.yaml'
    shutil.copyfile(meta_file, dst.joinpath(meta_file).as_posix())

    build_script = dst.joinpath('build0.sh')
    with open(build_script, 'w', encoding='utf8') as f:
        for fn in out_files:
            out_fn = os.path.splitext(fn)[0] + '.pdf' 
            build_code = ' '.join(['pandoc ', fn, '--metadata-file=meta.yaml', '-o', out_fn])
            f.write(build_code)
            f.write('\n')
    shutil.copyfile(build_script, os.path.splitext(build_script.as_posix())[0] + '.bat')

    out_files = ' '.join(out_files)
    build_code = ' '.join(['pandoc --toc -V documentclass=report', out_files, '--metadata-file=meta.yaml', '-o output.pdf']) 
    build_script = dst.joinpath('build.sh')
    with open(build_script, 'w', encoding='utf8') as f:
        f.write(build_code)
    shutil.copyfile(build_script, os.path.splitext(build_script.as_posix())[0] + '.bat')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='codebook', description='Convert source codes into a pdf file using pandoc')
    argparser.add_argument('src', help='Root path of source code')
    argparser.add_argument('dst', help='Destination path of converted code')

    args = argparser.parse_args()
    # print(args.src, args.dst)
    main(args.src, args.dst)
