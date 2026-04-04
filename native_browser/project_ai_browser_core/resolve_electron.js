try {
    console.log('Resolve path:', require.resolve('electron'));
    const electron = require('electron');
    console.log('Type of electron:', typeof electron);
    console.log('Keys:', Object.keys(electron));
} catch (e) {
    console.error('Resolution failed:', e);
}
