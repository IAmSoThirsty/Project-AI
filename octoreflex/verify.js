/**
 * Native Node.js Verification Engine for Project-AI Jurisdictions
 * 
 * This script runs the Thirsty-Lang test suites directly in Node.js,
 * leveraging the patched interpreter to bypass Windows sandbox-exec requirements.
 */

const { ThirstyInterpreter } = require('../../Thirsty-Lang/src/index');
const path = require('path');
const fs = require('fs');

async function verify() {
    console.log('\x1b[36m%s\x1b[0m', '--- Project-AI: Multi-Jurisdiction Verification Hub (Direct Node) ---');

    const interpreter = new ThirstyInterpreter({
        security: true,
        securityMode: 'defensive'
    });

    // Mock logger for cleaner output
    interpreter.logger.info = (msg) => console.log(`[\x1b[34mINFO\x1b[0m] ${msg}`);
    interpreter.logger.warn = (msg) => console.warn(`[\x1b[33mWARN\x1b[0m] ${msg}`);
    interpreter.logger.error = (msg) => console.error(`[\x1b[31mERROR\x1b[0m] ${msg}`);

    // Standard pour implementation redirects to console
    const originalExecute = interpreter.execute.bind(interpreter);

    const runTestSuite = (testPath) => {
        const absolutePath = path.resolve(testPath);
        console.log(`\n\x1b[35mExecuting Suite: ${path.basename(testPath)}\x1b[0m`);
        const code = fs.readFileSync(absolutePath, 'utf8');

        // Update interpreter context for relative imports
        interpreter.currentFile = absolutePath;

        try {
            interpreter.execute(code);
            console.log(`\x1b[32mPASS: ${path.basename(testPath)}\x1b[0m`);
            return true;
        } catch (e) {
            console.error(`\x1b[31mFAIL: ${path.basename(testPath)}\x1b[0m`);
            console.error(e.message);
            return false;
        }
    };

    const suites = [
        'test/jurisdiction0_test.tarl',
        'test/jurisdiction1_test.tarl',
        'test/jurisdiction2_test.tarl'
    ];

    let allPassed = true;
    for (const suite of suites) {
        if (!runTestSuite(suite)) {
            allPassed = false;
        }
    }

    console.log('\n\x1b[36m%s\x1b[0m', '------------------------------------------------------------');
    if (allPassed) {
        console.log('\x1b[32m%s\x1b[0m', 'RESULT: ALL JURISDICTIONS (0, 1, 2) VERIFIED SUCCESSFULLY');
    } else {
        console.log('\x1b[31m%s\x1b[0m', 'RESULT: VERIFICATION FAILED');
        process.exit(1);
    }
}

verify().catch(err => {
    console.error('Fatal Hub Failure:', err);
    process.exit(1);
});
