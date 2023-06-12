import os,re,shutil

data_dir = "sopia"
out_dir = "sopia_xpl"
shutil.rmtree(out_dir, ignore_errors=True)
for root, dirs, files in os.walk(data_dir):
    for dir in dirs:
        os.makedirs(os.path.join(out_dir,os.path.relpath(os.path.join(root,dir),data_dir)),exist_ok=True)
    for file in files:
        if re.findall("xpl",file,flags=re.IGNORECASE):
            try:
                shutil.copyfile(os.path.join(root,file),os.path.join(out_dir,os.path.relpath(os.path.join(root,file),data_dir)))
            except:
                print(f"File {os.path.join(root,file)} could not be copied to {os.path.join(out_dir,os.path.relpath(os.path.join(root,data_dir),root))}.\n")