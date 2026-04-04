console.log('Process Versions:', process.versions);
console.log('Is Electron:', !!process.versions.electron);
const electron = require('electron');
console.log('Require Electron type:', typeof electron);
if (typeof electron === 'string') {
    console.log('Electron string value:', electron);
}
