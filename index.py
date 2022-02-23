import zipfile,os,re,shutil,sys

class Textchanger:
    def __init__(self,folder_loc):
        
            self.folder_loc=folder_loc
            self.input_file_path=os.path.join("OEBPS","package.opf")
            self.output_file_path=os.path.join("OEBPS","content.opf")
            self.container_file_path=os.path.join("META-INF","container.xml")
            self.old_text=['<?xml version="1.0" encoding="UTF-8"?>','<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="ISBN9781550655704">']
            self.new_text=['<?xml version="1.0" encoding="UTF-9"?>','<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en" unique-identifier="BookID">']
            self.books=[]
            self.getAllBooks()
    

    def getAllBooks(self):
        files=os.listdir(self.folder_loc)
        for file in files:
            if ".epub" in file:
                self.books.append(file)
        if(len(self.books)>0):
            self.changeContent()
        else:   
            print("No epub files present at ",self.folder_loc)

    def checkFileExists(self,file_path):
        if(os.path.exists(file_path)):
            return True
        else:
            print("File not found for",file_path)

    def changeContent(self):
        for book_name in self.books:
            
            self.ePubUnZip(book_name,self.folder_loc)
            
            book_folder=book_name.replace(".epub","")

            self.replaceText(os.path.join(self.folder_loc,book_folder,self.input_file_path))
            
            self.renameFile(book_folder)
            
            self.rewriteMetaInfo(book_folder)
            
            self.ePubZip(book_name,self.folder_loc)


    def ePubZip(self,book_name,path):

        folder = book_name.replace('.epub', '')
        if os.path.isfile(os.path.join(path,folder,'mimetype')):
            with open(os.path.join(self.folder_loc+folder,self.container_file_path), 'r') as r:
                filePaths = re.search(r'full-path="([^"]*)/([^"]*).opf"', r.read()).group(1)
            with zipfile.ZipFile(os.path.join(path,folder+'.epub'), 'w') as myzip:
                myzip.writestr('mimetype', 'application/epub+zip')
            with zipfile.ZipFile(os.path.join(path,folder+'.epub'), 'a') as myzip:
                for base, dirs, files in os.walk(os.path.join(path,folder+'META-INF')):
                    for ifile in files:
                        fn = os.path.join(base, ifile)
                        myzip.write(fn, os.path.join(base.replace(os.path.join(path,folder), ''), ifile))
            with zipfile.ZipFile(os.path.join(path,folder+'.epub'), 'a') as myzip:
                for base, dirs, files in os.walk(os.path.join(path,folder,filePaths)):
                    for ifile in files:
                        fn = os.path.join(base, ifile)
                        if not fn.endswith('Thumbs.db') and not fn.endswith('debug.log'):
                            myzip.write(fn, os.path.join(base.replace(os.path.join(path,folder), ''), ifile))
        
        shutil.rmtree(os.path.join(path,folder))
        return True

    def ePubUnZip(self,book_name, path):
        z = zipfile.ZipFile(os.path.join(path,book_name))
        for name in z.namelist():
            output = str(os.path.join(path,book_name.replace('.epub', '')))
            z.extract(name, output)
        z.close()
        os.remove(os.path.join(path,book_name))
        return True

    def replaceText(self,file_path):
        if(self.checkFileExists(file_path)):
            file_obj=open(file_path,"r+")
            content=file_obj.read()
            for index in range(len(self.old_text)):
                content=content.replace(self.old_text[index],self.new_text[index])
            file_obj.close()
            file_obj=open(file_path,"w")
            file_obj.write(str(content))
            file_obj.close()


    def renameFile(self,book_folder):
        old_name=os.path.join(self.folder_loc,book_folder,self.input_file_path);
        new_name=os.path.join(self.folder_loc,book_folder,self.output_file_path);
        if(self.checkFileExists(old_name)):
            os.rename(old_name,new_name)

    def rewriteMetaInfo(self,book_folder):
        file_path=os.path.join(self.folder_loc,book_folder,self.container_file_path)
        if(self.checkFileExists(file_path)):
            file_obj=open(file_path,"r")
            content=file_obj.read()
            content=content.replace('full-path="OEBPS/package.opf"','full-path="OEBPS/content.opf"')
            file_obj.close()
            file_obj=open(file_path,"w")
            file_obj.write(str(content))
            file_obj.close()

if(len(sys.argv)>=2):
    file_path=sys.argv[1]
    if(os.path.exists(file_path)):
        obj=Textchanger(file_path)
    else:
        print("No Path Found for ",file_path)
else:
    print("Plse pass the folder location by \n\n'python index.py folder_loc'\n\n")