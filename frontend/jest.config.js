const {defaults} = require('jest-config');
module.exports = {
    "clearMocks": true,
    "transform": {
        "\\.[jt]sx?$": "esbuild-jest"
    },
    "transformIgnorePatterns": [
        "node_modules/(?!(three|three/examples/jsm/loaders/OBJLoader)/)"
    ]
};
