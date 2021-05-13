git clone https://github.com/foxxyz/multibrowse.git multibrowse-source
cd multibrowse-source
sudo apt install -y lxrandr
pip install -v pyinstaller
pyinstaller --onefile multibrowse.py
mv dist/multibrowse ..