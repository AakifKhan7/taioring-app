const { app, BrowserWindow } = require('electron');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
        },
        icon: path.resolve(__dirname, 'favicon.ico'),
        show: false, // Start window hidden to prevent flash
    });

    const flaskURL = 'http://127.0.0.1:5000';

    const checkFlask = () => {
        console.log('Checking if Flask server is ready...');
        http.get(flaskURL, (res) => {
            if (res.statusCode === 200) {
                console.log('Flask server is ready. Loading...');
                mainWindow.loadURL(flaskURL);
                mainWindow.show(); // Show window when Flask is ready
            } else {
                console.log(`Unexpected status code: ${res.statusCode}`);
                setTimeout(checkFlask, 500); // Retry
            }
        }).on('error', (err) => {
            console.error('Flask server not ready. Retrying...');
            setTimeout(checkFlask, 500); // Retry
        });
    };

    checkFlask();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function startFlask() {
    console.log('Starting Flask server...');
    
    // Use pythonw.exe to avoid opening a console window
    const flaskProcess = spawn('pythonw', ['./flask-app/app.py'], {
        stdio: 'ignore', // Ignore stdio so the console window won't appear
        detached: true, // Run the process in the background
    });

    flaskProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Flask process exited with code ${code}`);
        }
    });

    return flaskProcess;
}

app.whenReady().then(() => {
    startFlask();
    createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
