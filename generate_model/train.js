const fs = require('fs');
const path = require('path');
const physicsFilePath = path.join(__dirname, '..', 'js', 'physics.js');
const physicsCode = fs.readFileSync(physicsFilePath, 'utf8');

// 在當前 Node 環境執行該代碼，這樣 Physics 物件就會被定義
eval(physicsCode);

// 檢查 SCHEMA 是否也需要從 params.js 獲取 (如果 train.js 沒定義 SCHEMA)
const SCHEMA = {
    logM: { min: 10, max: 15 },
    rd: { min: 0.5, max: 12 },
    sfr: { min: -2, max: 3 }
};

function generateTrainingData(count = 10000) {
    console.log(`🚀 正在產生 ${count} 筆訓練數據...`);
    let dataset = [];

    for (let i = 0; i < count; i++) {
        let inputParams = {
            logM: 10 + Math.random() * 5,
            rd: 0.5 + Math.random() * 11.5,
            sfr: -2.0 + Math.random() * 5.0,
            conc: 8, bd: 0.2, agn: 0.1, snfb: 0.1, qprob: 0.2,
            smbh: 7.5, sersic: 1.5, mhi: 9.5, mh2: 8.8, imf: 'kroupa'
        };
        let result = Physics.compute(inputParams);
        dataset.push({
            input: {
                logM: parseFloat(inputParams.logM.toFixed(4)),
                rd: parseFloat(inputParams.rd.toFixed(4)),
                sfr: parseFloat(inputParams.sfr.toFixed(4))
            },
            output: {
                Rv: parseFloat(result.Rv.toFixed(4)),
                V2: parseFloat(result.V2.toFixed(4)),
                Ms: parseFloat(result.Ms.toExponential(4))
            }
        });
    }
    const dataFolder = path.join(__dirname, '..', 'data');
    if (!fs.existsSync(dataFolder)) fs.mkdirSync(dataFolder); 
    const outputPath = path.join(dataFolder, 'data_10000.json');
    fs.writeFileSync(outputPath, JSON.stringify(dataset, null, 2));
}

generateTrainingData(10000);