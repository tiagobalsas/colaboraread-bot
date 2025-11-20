#!/bin/bash

# Instalar dependências
apt-get update
apt-get install -y wget unzip

# Baixar e instalar Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Baixar ChromeDriver
wget -q https://storage.googleapis.com/chrome-for-testing-public/142.0.7394.0/linux64/chromedriver-linux64.zip
unzip -o chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64*

echo "Chrome e ChromeDriver instalados!"
