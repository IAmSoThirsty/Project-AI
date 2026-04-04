const electron = require('electron');
console.log('Electron module keys:', Object.keys(electron));
if (electron.app) {
    console.log('App module found.');
} else {
    console.error('App module is UNDEFINED!');
}
