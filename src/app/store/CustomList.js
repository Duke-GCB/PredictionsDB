export const CUSTOM_GENE_LIST = 'Custom Gene List';
export const CUSTOM_RANGES_LIST = 'Custom Ranges List';

var SETTINGS = [];
SETTINGS[CUSTOM_GENE_LIST] = {
    sampleData: "WASH7P\nSAMD11\nRIMKLA",
    encode: encodeGeneListValue,
    decode: decodeGeneListValue
};
SETTINGS[CUSTOM_RANGES_LIST] = {
    sampleData: "10413\t11027\tchr1\n520413\t521391\tchr2",
    encode: noop,
    decode: noop,
};

function lookup_settings(type) {
    if (type in SETTINGS) {
        return SETTINGS[type];
    } else {
        return {
            sampleData: "",
            encode: noop,
            decode: noop,
        };
    }
}

function encodeGeneListValue(value) {
    return value.split('\n').join('%2C');
}

function decodeGeneListValue(value) {
    return value.split('%2C').join('\n');
}

function noop(value) {
    return value;
}

export class CustomListData {
    constructor(type) {
        var settings = lookup_settings(type);
        this.type = type;
        this.sampleData = settings.sampleData;
        this.encodeFunc = settings.encode;
        this.decodeFunc = settings.decode;
    }

    isGeneList() {
        return this.type == CUSTOM_GENE_LIST;
    }

    encode(value) {
        return this.encodeFunc(value);
    }

    decode(value) {
        return this.decodeFunc(value);
    }
}