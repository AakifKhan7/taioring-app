const { app, BrowserWindow } = require('electron');
const path = require('path');
const http = require('http');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
        },
    });

    const flaskURL = 'http://127.0.0.1:5000';

    const checkFlask = () => {
        http.get(flaskURL, (res) => {
            if (res.statusCode === 200) {
                mainWindow.loadURL(flaskURL);
            }
        }).on('error', () => {
            setTimeout(checkFlask, 500); // Retry until Flask is ready
        });
    };

    checkFlask();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
