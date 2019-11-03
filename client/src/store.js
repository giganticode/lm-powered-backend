// model cache
let models = {};
let modelsJson = localStorage.getItem('models') || "{}"; 

// code-input cache
let lastDebuggerInput = localStorage.getItem('lastDebuggerInput') || "public class Test {\n    public static void main(String[] args) {\n\n    }\n}";
let lastComparatorInput = localStorage.getItem('lastComparatorInput') || "public class Test {\n    public static void main(String[] args) {\n\n    }\n}";
let lastPredictionInput = localStorage.getItem('lastPredictionInput') || "public class Test {\n    public static void main(String[] args) {\n\n    }\n}";
let lastSearchInput = localStorage.getItem('lastSearchInput') || "public class Test {\n    public static void main(String[] args) {\n\n    }\n}";

// selected models
let currentModel = localStorage.getItem('currentModel') || 'langmodel-large-split_10k_1_512_190926.120146';
let currentModel2 = localStorage.getItem('currentModel2') || 'langmodel-large-split_10k_1_512_190926.120146';

// tokenTypes and metrics
let tokenTypesJson = localStorage.getItem('tokenTypesJson') || `["all", "only_comments", "all_but_comments"]`;
let metricsJson = localStorage.getItem('metricsJson') || `["full_token_entropy", "mrr", "subtoken_entropy"]`;
let tokenTypes = [];
let metrics = [];

// default color mappings
let defaultColorMappingEntropy = [
    {'min': 0, 'max': 2, 'color': 'green'}, 
    {'min': 2, 'max': 4, 'color': 'rgb(126, 128, 0)'}, 
    {'min': 4, 'max': 8, 'color': 'orange'}, 
    {'min': 8, 'max': 16, 'color': 'rgb(255, 72, 0)'}, 
    {'min': 16, 'max': 25, 'color': 'red'}
];
let defaultColorMappingPercent = [
    {'min': 0, 'max': 10, 'color': 'green'}, 
    {'min': 10, 'max': 25, 'color': 'rgb(126, 128, 0)'}, 
    {'min': 25, 'max': 75, 'color': 'orange'}, 
    {'min': 75, 'max': 200, 'color': 'rgb(255, 72, 0)'}, 
    {'min': 200, 'max': 5000, 'color': 'red'}
];

let colorMappingEntropyJson = localStorage.getItem('colorMappingEntropy') || JSON.stringify(defaultColorMappingEntropy);
let colorMappingPercentJson = localStorage.getItem('colorMappingPercent') || JSON.stringify(defaultColorMappingPercent);

let colorMappingEntropy = [];
let colorMappingPercent = [];

try {
    models = JSON.parse(modelsJson);
} catch (e) {
    console.error("could not parse models from JSON");
}

try {
    metrics = JSON.parse(metricsJson);
} catch (e) {
    console.error("could not parse metrics from JSON");
}

try {
    tokenTypes = JSON.parse(tokenTypesJson);
} catch (e) {
    console.error("could not parse tokentypes from JSON");
}

try {
    colorMappingEntropy = JSON.parse(colorMappingEntropyJson);
} catch (e) {
    colorMappingEntropy = JSON.parse(JSON.stringify(defaultColorMappingEntropy));
}

try {
    colorMappingPercent = JSON.parse(colorMappingPercentJson);
} catch (e) {
    colorMappingPercent = JSON.parse(JSON.stringify(defaultColorMappingPercent));
}

export default {
    state: {
        models: models,
        lastDebuggerInput: lastDebuggerInput,
        lastComparatorInput: lastComparatorInput,
        lastPredictionInput: lastPredictionInput,
        lastSearchInput: lastSearchInput,
        currentModel: currentModel,
        currentModel2: currentModel2,
        defaultColorMappingEntropy: defaultColorMappingEntropy,
        defaultColorMappingPercent: defaultColorMappingPercent,
        colorMappingEntropy: colorMappingEntropy,
        colorMappingPercent: colorMappingPercent,
        metrics: metrics,
        tokenTypes: tokenTypes,
    },
    getters: {
        models(state) {
            return state.models;
        },
        lastDebuggerInput(state) {
            return state.lastDebuggerInput;
        },
        lastComparatorInput(state) {
            return state.lastComparatorInput;
        },
        lastPredictionInput(state) {
            return state.lastPredictionInput;
        },
        lastSearchInput(state) {
            return state.lastSearchInput;
        },
        currentModel(state) {
            return state.currentModel;
        },
        currentModel2(state) {
            return state.currentModel2;
        },
        defaultColorMappingEntropy(state) {
            return state.defaultColorMappingEntropy;
        },
        defaultColorMappingPercent(state) {
            return state.defaultColorMappingPercent;
        },
        colorMappingEntropy(state) {
            return state.colorMappingEntropy;
        },
        colorMappingPercent(state) {
            return state.colorMappingPercent;
        },
        metrics(state) {
            return state.metrics;
        },
        tokenTypes(state) {
            return state.tokenTypes;
        }
    },
    mutations: {
        modelsDownloaded(state, models) {
            let modelsObj = {};
            for (let key in models) {
                let model = models[key];
                modelsObj[model.id] = model;
            }
            state.models = modelsObj;
            localStorage.setItem("models", JSON.stringify(modelsObj));
        },
        lastDebuggerInput(state, lastDebuggerInput) {
            state.lastDebuggerInput = lastDebuggerInput;
            localStorage.setItem('lastDebuggerInput', lastDebuggerInput);
        },
        lastComparatorInput(state, lastComparatorInput) {
            state.lastComparatorInput = lastComparatorInput;
            localStorage.setItem('lastComparatorInput', lastComparatorInput);
        },
        lastPredictionInput(state, lastPredictionInput) {
            state.lastPredictionInput = lastPredictionInput;
            localStorage.setItem('lastPredictionInput', lastPredictionInput);
        },
        lastSearchInput(state, lastSearchInput) {
            state.lastSearchInput = lastSearchInput;
            localStorage.setItem('lastSearchInput', lastSearchInput);
        },
        currentModel(state, currentModel) {
            state.currentModel = currentModel;
            localStorage.setItem('currentModel', currentModel);
        },
        currentModel2(state, currentModel2) {
            state.currentModel2 = currentModel2;
            localStorage.setItem('currentModel2', currentModel2);
        },
        colorMappingEntropy(state, colorMappingEntropy) {
            state.colorMappingEntropy = colorMappingEntropy;
            localStorage.setItem('colorMappingEntropy', colorMappingEntropy);
        },
        colorMappingPercent(state, colorMappingPercent) {
            state.colorMappingPercent = colorMappingPercent;
            localStorage.setItem('colorMappingPercent', colorMappingPercent);
        }       
    },
    actions: {
        login(context){
            context.commit("login");
        }
    }
};