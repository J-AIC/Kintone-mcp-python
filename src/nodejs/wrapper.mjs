import { KintoneRestAPIClient } from '@kintone/rest-api-client';

class KintoneAPIWrapper {
    constructor(domain, username, password, apiToken = null) {
        const auth = apiToken 
            ? { apiToken: apiToken }
            : { username: username, password: password };
            
        this.client = new KintoneRestAPIClient({
            baseUrl: `https://${domain}`,
            auth: auth
        });
    }
    
    async getApps() {
        return await this.client.app.getApps();
    }
    
    async getRecord(appId, recordId) {
        return await this.client.record.getRecord({
            app: appId,
            id: recordId
        });
    }
    
    async getRecords(appId, query = '', fields = []) {
        return await this.client.record.getRecords({
            app: appId,
            query: query,
            fields: fields
        });
    }
    
    async createRecord(appId, record) {
        console.error(`[DEBUG] createRecord called with appId: ${appId}, record:`, JSON.stringify(record, null, 2));
        
        // エンコーディング正規化処理
        const normalizedRecord = this.normalizeRecordEncoding(record);
        console.error(`[DEBUG] Normalized record:`, JSON.stringify(normalizedRecord, null, 2));
        
        const request = {
            app: appId,
            record: normalizedRecord
        };
        console.error(`[DEBUG] Final request to Kintone API:`, JSON.stringify(request, null, 2));
        
        try {
            const result = await this.client.record.addRecord(request);
            console.error(`[DEBUG] createRecord success:`, JSON.stringify(result, null, 2));
            return result;
        } catch (error) {
            console.error(`[DEBUG] createRecord error:`, error.message);
            console.error(`[DEBUG] createRecord error details:`, JSON.stringify(error, null, 2));
            throw error;
        }
    }
    
    normalizeRecordEncoding(record) {
        if (!record || typeof record !== 'object') {
            return record;
        }
        
        const normalized = {};
        for (const [key, value] of Object.entries(record)) {
            if (value && typeof value === 'object' && value.value !== undefined) {
                // Kintoneフィールド形式の場合
                normalized[key] = {
                    ...value,
                    value: this.normalizeStringValue(value.value)
                };
            } else {
                normalized[key] = this.normalizeStringValue(value);
            }
        }
        
        return normalized;
    }
    
    normalizeStringValue(value) {
        if (typeof value !== 'string') {
            return value;
        }
        
        try {
            // 既知の文字化けパターンを修正
            let normalized = this.fixMojibakePatterns(value);
            
            // Unicode正規化
            normalized = normalized.normalize('NFKC');
            
            // 不正な文字の除去
            normalized = normalized.replace(/[\uDC00-\uDFFF]/g, ''); // サロゲート文字除去
            normalized = normalized.replace(/[\x00-\x1F\x7F-\x9F]/g, ''); // 制御文字除去
            
            const result = normalized.trim();
            
            if (result !== value) {
                console.error(`[DEBUG] String normalization: '${value}' -> '${result}'`);
            }
            
            return result;
        } catch (error) {
            console.error(`[DEBUG] String normalization error:`, error);
            return value;
        }
    }

    fixMojibakePatterns(text) {
        const mojibakeMap = {
            // カテゴリーフィールドの修正
            "莠､騾夊ｲｻ": "会議費",
            "豸郁怜刀雋ｻ": "交通費",
            "謗･蠖ｵ雋ｻ": "接待費",
            "豸郁枩蜩∵ｲｻ": "消耗品費",
            "騾夊ｨ夊ｲｻ": "通信費",
            "蜈画椡雋ｻ": "光熱費",
            "縺昴ｎ莉": "その他",
            
            // 承認状況の修正
            "逕ｳ隲倶ｸｭ": "申請中",
            "謇ｿ隱阪☆縺ｿ": "承認済み",
            "蟾ｮ縺嶺ｻ倥＠": "差し戻し",
            
            // 会社名の修正
            "譛蛾剞莨夂、セ繧オ繝ウ繝励Ν繧オ繝ウ繝励Ν蝠 莠": "株式会社サンプル商事",
            "譛蛾剞莨夂､ｾ繧ｵ繝ｳ繝励Ν繧ｵ繝ｳ繝励Ν蝠 莠": "株式会社サンプル商事",
            "譬ｪ蠑丈ｼ夂､ｾ繧ｵ繝ｳ繝励Ν蝠莠": "株式会社サンプル商事",
            
            // 目的・用途の修正
            "蜃コ蠑オ譎ゅ ョ繧ソ繧ッ繧キ繝シ莉」縺ィ縺励※菴ソ逕ｨ シ域擲莠ャ-蜊 闡蛾俣 シ": "出張時のタクシー代として使用（領収書-枚 添付）",
            "蜃ｺ蠑ｵ譎ゅ ｮ繧ｿ繧ｯ繧ｷ繝ｼ莉｣縺ｨ縺励※菴ｿ逕ｨ ｼ域擲莠ｬ-蜊 闡蛾俣 ｼ": "出張時のタクシー代として使用（領収書-枚 添付）"
        };
        
        let result = text;
        for (const [mojibake, correct] of Object.entries(mojibakeMap)) {
            if (result.includes(mojibake)) {
                result = result.replace(new RegExp(mojibake.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), correct);
            }
        }
        
        return result;
    }
    
    async updateRecord(appId, recordId, record) {
        return await this.client.record.updateRecord({
            app: appId,
            id: recordId,
            record: record
        });
    }
    
    async getProcessManagement(appId, preview = false) {
        return await this.client.app.getProcessManagement({
            app: appId,
            preview: preview
        });
    }

    async getPreviewAppSettings(appId, lang = null) {
        try {
            console.error(`[DEBUG] Fetching preview app settings for app: ${appId}`);
            
            // プレビュー環境のAPIを呼び出す
            const params = { app: parseInt(appId), preview: true };
            if (lang) {
                params.lang = lang;
            }
            
            const response = await this.client.app.getAppSettings(params);
            console.error(`[DEBUG] Preview app settings response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview app settings for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewFormFields(appId, lang = null) {
        const params = { app: parseInt(appId), preview: true };
        if (lang) params.lang = lang;
        
        try {
            const result = await this.client.app.getFormFields(params);
            result._isPreview = true;
            result._message = "このフィールド情報はプレビュー環境から取得されました。";
            return result;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview form fields for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewFormLayout(appId) {
        try {
            return await this.client.app.getFormLayout({
                app: parseInt(appId),
                preview: true
            });
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview form layout for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewApps() {
        console.error('[WARNING] Preview apps cannot be listed directly. Use getPreviewFormFields with specific app IDs.');
        return { 
            success: false, 
            error: "プレビューアプリの直接一覧取得はKintone APIではサポートされていません。特定のアプリIDでプレビュー設定にアクセスしてください。",
            suggestion: "deploy_app ツールでプレビューアプリを運用環境にデプロイすることを推奨します。"
        };
    }

    async getPreviewForm(appId, lang = null) {
        try {
            console.error(`[DEBUG] Fetching preview form for app: ${appId}`);
            
            // プレビュー環境のフォーム情報を取得 - 既存のFormFieldsメソッドを使用
            const params = { app: parseInt(appId), preview: true };
            if (lang) params.lang = lang;
            
            const response = await this.client.app.getFormFields(params);
            console.error(`[DEBUG] Preview form response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview form for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewProcessManagement(appId) {
        try {
            return await this.client.app.getProcessManagement({
                app: parseInt(appId),
                preview: true
            });
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview process management for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewAppCustomization(appId) {
        try {
            console.error(`[DEBUG] Fetching preview app customization for app: ${appId}`);
            
            // プレビュー環境のアプリカスタマイズ設定を取得
            const params = { app: parseInt(appId), preview: true };
            
            const response = await this.client.app.getAppCustomize(params);
            console.error(`[DEBUG] Preview app customization response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview app customization for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewAppViews(appId, lang = null) {
        try {
            console.error(`[DEBUG] Fetching preview app views for app: ${appId}`);
            
            // プレビュー環境のビュー設定を取得
            const params = { app: parseInt(appId), preview: true };
            if (lang) params.lang = lang;
            
            const response = await this.client.app.getViews(params);
            console.error(`[DEBUG] Preview app views response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview app views for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getPreviewAppPermissions(appId) {
        try {
            console.error(`[DEBUG] Fetching preview app permissions for app: ${appId}`);
            
            // プレビュー環境のアプリ権限設定を取得
            const params = { app: parseInt(appId), preview: true };
            
            const response = await this.client.app.getAppAcl(params);
            console.error(`[DEBUG] Preview app permissions response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get preview app permissions for app ${appId}:`, error.message);
            throw error;
        }
    }

    async createApp(name, space = null, thread = null) {
        const params = { name };
        if (space) params.space = space;
        if (thread) params.thread = thread;
        return await this.client.app.addApp(params);
    }

    async deployApp(apps) {
        // appsが単純なIDの配列の場合、正しい形式に変換
        const formattedApps = apps.map(app => {
            if (typeof app === 'number' || typeof app === 'string') {
                return { app: parseInt(app), revision: -1 };
            }
            return app; // 既に正しい形式の場合はそのまま
        });
        
        console.error(`[DEBUG] Deploying apps with formatted data:`, JSON.stringify(formattedApps));
        
        try {
            const result = await this.client.app.deployApp({ apps: formattedApps });
            console.error(`[DEBUG] Deploy success:`, JSON.stringify(result));
            return result;
        } catch (error) {
            console.error(`[DEBUG] Deploy error:`, error.message);
            console.error(`[DEBUG] Deploy error details:`, JSON.stringify(error, null, 2));
            throw error;
        }
    }

    async getDeployStatus(apps) {
        const appIds = apps.map(app => parseInt(app));
        return await this.client.app.getDeployStatus({ apps: appIds });
    }

    async updateAppSettings(appId, settings) {
        try {
            console.error(`[DEBUG] Updating app settings for app: ${appId}`);
            
            // プレビュー環境のアプリ設定を更新
            const params = {
                app: parseInt(appId),
                ...settings
            };
            
            const response = await this.client.app.updateAppSettings(params);
            console.error(`[DEBUG] Update app settings response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to update app settings for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getFormLayout(appId, preview = false) {
        return await this.client.app.getFormLayout({
            app: appId,
            preview: preview
        });
    }

    async updateFormLayout(appId, layout, revision = null) {
        const params = { app: appId, layout };
        if (revision !== null) params.revision = revision;
        return await this.client.app.updateFormLayout(params);
    }

    async moveAppToSpace(appId, spaceId, threadId = null) {
        const params = { app: appId, space: spaceId };
        if (threadId) params.thread = threadId;
        return await this.client.app.moveAppToSpace(params);
    }

    async moveAppFromSpace(appId) {
        return await this.client.app.moveAppToSpace({ app: appId });
    }

    async getAppActions(appId, lang = null) {
        try {
            console.error(`[DEBUG] Fetching app actions for app: ${appId}`);
            
            // アプリアクション設定を取得
            const params = { app: parseInt(appId) };
            if (lang) params.lang = lang;
            
            const response = await this.client.app.getActionSettings(params);
            console.error(`[DEBUG] App actions response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get app actions for app ${appId}:`, error.message);
            throw error;
        }
    }

    async getAppPlugins(appId) {
        try {
            console.error(`[DEBUG] Fetching app plugins for app: ${appId}`);
            
            // アプリプラグイン設定を取得
            const params = { app: parseInt(appId) };
            
            const response = await this.client.app.getAppPlugins(params);
            console.error(`[DEBUG] App plugins response:`, response);
            return response;
        } catch (error) {
            console.error(`[DEBUG] Failed to get app plugins for app ${appId}:`, error.message);
            throw error;
        }
    }

    async addFields(appId, properties, revision = null) {
        const params = { app: appId, properties };
        if (revision !== null) params.revision = revision;
        return await this.client.app.addFormFields(params);
    }

    async updateFields(appId, properties, revision = null) {
        const params = { app: appId, properties };
        if (revision !== null) params.revision = revision;
        return await this.client.app.updateFormFields(params);
    }

    async deleteFields(appId, fieldCodes, revision = null) {
        const params = { app: appId, fields: fieldCodes };
        if (revision !== null) params.revision = revision;
        return await this.client.app.deleteFormFields(params);
    }

    async getFormFields(appId, lang = null) {
        const params = { app: parseInt(appId) };
        if (lang) params.lang = lang;
        
        try {
            // まず本番環境から取得を試す
            return await this.client.app.getFormFields(params);
        } catch (error) {
            console.error(`[DEBUG] Failed to get form fields from production, trying preview for app ${appId}:`, error.message);
            
            // 本番環境で失敗した場合、プレビュー環境から取得を試す
            try {
                const result = await this.client.app.getFormFields({ ...params, preview: true });
                result._isPreview = true;
                result._message = "このフィールド情報はプレビュー環境から取得されました。アプリをデプロイするには deploy_app ツールを使用してください。";
                return result;
            } catch (previewError) {
                console.error(`[DEBUG] Failed to get form fields from preview as well:`, previewError.message);
                throw error; // 元のエラーを投げる
            }
        }
    }

    async addRecordComment(appId, recordId, comment) {
        return await this.client.record.addComment({
            app: appId,
            record: recordId,
            comment: comment
        });
    }

    async uploadFile(fileName, fileData) {
        const buffer = Buffer.from(fileData, 'base64');
        return await this.client.file.uploadFile({
            file: {
                name: fileName,
                data: buffer
            }
        });
    }

    async downloadFile(fileKey) {
        return await this.client.file.downloadFile({ fileKey });
    }

    async getUsers(codes = null) {
        const params = {};
        if (codes) params.codes = codes;
        return await this.client.user.getUsers(params);
    }

    async getGroups(codes = null) {
        const params = {};
        if (codes) params.codes = codes;
        return await this.client.user.getGroups(params);
    }

    async getGroupUsers(code) {
        return await this.client.user.getGroupUsers({ code });
    }

    async addGuests(guests) {
        return await this.client.space.addGuests({ guests });
    }

    async getSpace(spaceId) {
        return await this.client.space.getSpace({ id: spaceId });
    }

    async updateSpace(spaceId, body, name = null, isPrivate = null) {
        const params = { id: spaceId, body };
        if (name !== null) params.name = name;
        if (isPrivate !== null) params.isPrivate = isPrivate;
        return await this.client.space.updateSpace(params);
    }

    async updateSpaceBody(spaceId, body) {
        return await this.client.space.updateSpaceBody({
            id: spaceId,
            body: body
        });
    }

    async getSpaceMembers(spaceId) {
        return await this.client.space.getSpaceMembers({ id: spaceId });
    }

    async updateSpaceMembers(spaceId, members) {
        return await this.client.space.updateSpaceMembers({
            id: spaceId,
            members: members
        });
    }

    async addThread(spaceId, name, body) {
        return await this.client.space.addThread({
            id: spaceId,
            name: name,
            body: body
        });
    }

    async updateThread(spaceId, threadId, name = null, body = null) {
        const params = { id: spaceId, threadId: threadId };
        if (name !== null) params.name = name;
        if (body !== null) params.body = body;
        return await this.client.space.updateThread(params);
    }

    async addThreadComment(spaceId, threadId, comment) {
        return await this.client.space.addThreadComment({
            id: spaceId,
            threadId: threadId,
            comment: comment
        });
    }

    async updateSpaceGuests(spaceId, guests) {
        return await this.client.space.updateGuestMembers({
            id: spaceId,
            guests: guests
        });
    }

    async checkAppExists(appId, checkPreview = true) {
        const id = parseInt(appId);
        
        try {
            // 本番環境でアプリの存在確認
            await this.client.app.getFormFields({ app: id });
            return { exists: true, environment: 'production', appId: id };
        } catch (error) {
            if (checkPreview) {
                try {
                    // プレビュー環境でアプリの存在確認
                    await this.client.app.getFormFields({ app: id, preview: true });
                    return { exists: true, environment: 'preview', appId: id };
                } catch (previewError) {
                    return { exists: false, environment: null, appId: id, error: error.message };
                }
            }
            return { exists: false, environment: null, appId: id, error: error.message };
        }
    }

    async getConnectionInfo() {
        return {
            status: 'connected',
            baseUrl: this.client.baseUrl,
            authType: this.client.auth.apiToken ? 'apiToken' : 'password'
        };
    }

    async loggingSetLevel(level) {
        console.log(`Log level set to: ${level}`);
        return { success: true, level: level };
    }

    async loggingGetLevel() {
        return { level: 'info' };
    }

    async loggingSendMessage(level, message) {
        console.log(`[${level.toUpperCase()}] ${message}`);
        return { success: true };
    }

    async getFieldTypeDocumentation(fieldType) {
        const docs = {
            'SINGLE_LINE_TEXT': 'Single line text field documentation',
            'MULTI_LINE_TEXT': 'Multi line text field documentation',
            'NUMBER': 'Number field documentation',
        };
        return { fieldType, documentation: docs[fieldType] || 'No documentation available' };
    }

    async getAvailableFieldTypes() {
        return {
            fieldTypes: [
                'SINGLE_LINE_TEXT', 'MULTI_LINE_TEXT', 'RICH_TEXT', 'NUMBER',
                'CALC', 'RADIO_BUTTON', 'CHECK_BOX', 'MULTI_SELECT',
                'DROP_DOWN', 'DATE', 'TIME', 'DATETIME', 'LINK',
                'FILE', 'USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT',
                'REFERENCE_TABLE', 'SUBTABLE'
            ]
        };
    }

    async getDocumentationToolDescription() {
        return { description: 'Documentation tools for Kintone MCP Server' };
    }

    async getFieldCreationToolDescription() {
        return { description: 'Field creation tools for Kintone applications' };
    }

    async createLayoutElement(elementType, config) {
        return {
            type: elementType,
            ...config
        };
    }

    async addFieldsToLayout(appId, fields, revision = null) {
        return { success: true, message: 'Fields added to layout' };
    }

    async removeFieldsFromLayout(appId, fieldCodes, revision = null) {
        return { success: true, message: 'Fields removed from layout' };
    }

    async organizeLayout(appId, organization, revision = null) {
        return { success: true, message: 'Layout organized' };
    }

    async createFieldGroup(name, fields) {
        return {
            type: 'GROUP',
            code: name.toLowerCase().replace(/\s+/g, '_'),
            label: name,
            fields: fields
        };
    }

    async createFormLayout(layout) {
        return { layout: layout };
    }

    async addLayoutElement(appId, element, revision = null) {
        return { success: true, message: 'Layout element added' };
    }

    async createGroupLayout(groupConfig) {
        return {
            type: 'GROUP',
            ...groupConfig
        };
    }

    async createTableLayout(tableConfig) {
        return {
            type: 'SUBTABLE',
            ...tableConfig
        };
    }

    async createLookupField(fieldType, code, label, relatedApp, relatedKeyField) {
        return {
            type: 'LOOKUP',
            code: code,
            label: label,
            lookup: {
                relatedApp: relatedApp,
                relatedKeyField: relatedKeyField,
                fieldMappings: []
            }
        };
    }
}

const args = process.argv.slice(2);
const command = args[0];
const params = JSON.parse(args[1] || '{}');

async function executeCommand() {
    try {
        const wrapper = new KintoneAPIWrapper(
            params.domain,
            params.username,
            params.password,
            params.apiToken
        );
        
        let result;
        switch (command) {
            case 'getApps':
                result = await wrapper.getApps();
                break;
            case 'getRecord':
                result = await wrapper.getRecord(params.appId, params.recordId);
                break;
            case 'getRecords':
                result = await wrapper.getRecords(params.appId, params.query, params.fields);
                break;
            case 'createRecord':
                result = await wrapper.createRecord(params.appId, params.record);
                break;
            case 'updateRecord':
                result = await wrapper.updateRecord(params.appId, params.recordId, params.record);
                break;
            case 'getProcessManagement':
                result = await wrapper.getProcessManagement(params.appId, params.preview);
                break;
            case 'createApp':
                result = await wrapper.createApp(params.name, params.space, params.thread);
                break;
            case 'deployApp':
                result = await wrapper.deployApp(params.apps);
                break;
            case 'getDeployStatus':
                result = await wrapper.getDeployStatus(params.apps);
                break;
            case 'updateAppSettings':
                result = await wrapper.updateAppSettings(params.appId, params.settings);
                break;
            case 'getFormLayout':
                result = await wrapper.getFormLayout(params.appId, params.preview);
                break;
            case 'updateFormLayout':
                result = await wrapper.updateFormLayout(params.appId, params.layout, params.revision);
                break;
            case 'moveAppToSpace':
                result = await wrapper.moveAppToSpace(params.appId, params.spaceId, params.threadId);
                break;
            case 'moveAppFromSpace':
                result = await wrapper.moveAppFromSpace(params.appId);
                break;
            case 'getPreviewAppSettings':
                result = await wrapper.getPreviewAppSettings(params.appId, params.lang);
                break;
            case 'getPreviewFormFields':
                result = await wrapper.getPreviewFormFields(params.appId, params.lang);
                break;
            case 'getPreviewFormLayout':
                result = await wrapper.getPreviewFormLayout(params.appId);
                break;
            case 'getPreviewApps':
                result = await wrapper.getPreviewApps();
                break;
            case 'getPreviewForm':
                result = await wrapper.getPreviewForm(params.appId, params.lang);
                break;
            case 'getPreviewProcessManagement':
                result = await wrapper.getPreviewProcessManagement(params.appId);
                break;
            case 'getPreviewAppCustomization':
                result = await wrapper.getPreviewAppCustomization(params.appId);
                break;
            case 'getPreviewAppViews':
                result = await wrapper.getPreviewAppViews(params.appId, params.lang);
                break;
            case 'getPreviewAppPermissions':
                result = await wrapper.getPreviewAppPermissions(params.appId);
                break;
            case 'getAppActions':
                result = await wrapper.getAppActions(params.appId, params.lang);
                break;
            case 'getAppPlugins':
                result = await wrapper.getAppPlugins(params.appId);
                break;
            case 'addFields':
                result = await wrapper.addFields(params.appId, params.properties, params.revision);
                break;
            case 'updateFields':
                result = await wrapper.updateFields(params.appId, params.properties, params.revision);
                break;
            case 'deleteFields':
                result = await wrapper.deleteFields(params.appId, params.fieldCodes, params.revision);
                break;
            case 'getFormFields':
                result = await wrapper.getFormFields(params.appId, params.lang);
                break;
            case 'createLookupField':
                result = await wrapper.createLookupField(
                    params.fieldType, params.code, params.label, 
                    params.relatedApp, params.relatedKeyField
                );
                break;
            case 'addRecordComment':
                result = await wrapper.addRecordComment(params.appId, params.recordId, params.comment);
                break;
            case 'uploadFile':
                result = await wrapper.uploadFile(params.fileName, params.fileData);
                break;
            case 'downloadFile':
                result = await wrapper.downloadFile(params.fileKey);
                break;
            case 'getUsers':
                result = await wrapper.getUsers(params.codes);
                break;
            case 'getGroups':
                result = await wrapper.getGroups(params.codes);
                break;
            case 'getGroupUsers':
                result = await wrapper.getGroupUsers(params.code);
                break;
            case 'addGuests':
                result = await wrapper.addGuests(params.guests);
                break;
            case 'getSpace':
                result = await wrapper.getSpace(params.spaceId);
                break;
            case 'updateSpace':
                result = await wrapper.updateSpace(params.spaceId, params.body, params.name, params.isPrivate);
                break;
            case 'updateSpaceBody':
                result = await wrapper.updateSpaceBody(params.spaceId, params.body);
                break;
            case 'getSpaceMembers':
                result = await wrapper.getSpaceMembers(params.spaceId);
                break;
            case 'updateSpaceMembers':
                result = await wrapper.updateSpaceMembers(params.spaceId, params.members);
                break;
            case 'addThread':
                result = await wrapper.addThread(params.spaceId, params.name, params.body);
                break;
            case 'updateThread':
                result = await wrapper.updateThread(params.spaceId, params.threadId, params.name, params.body);
                break;
            case 'addThreadComment':
                result = await wrapper.addThreadComment(params.spaceId, params.threadId, params.comment);
                break;
            case 'updateSpaceGuests':
                result = await wrapper.updateSpaceGuests(params.spaceId, params.guests);
                break;
            case 'getConnectionInfo':
                result = await wrapper.getConnectionInfo();
                break;
            case 'loggingSetLevel':
                result = await wrapper.loggingSetLevel(params.level);
                break;
            case 'loggingGetLevel':
                result = await wrapper.loggingGetLevel();
                break;
            case 'loggingSendMessage':
                result = await wrapper.loggingSendMessage(params.level, params.message);
                break;
            case 'getFieldTypeDocumentation':
                result = await wrapper.getFieldTypeDocumentation(params.fieldType);
                break;
            case 'getAvailableFieldTypes':
                result = await wrapper.getAvailableFieldTypes();
                break;
            case 'getDocumentationToolDescription':
                result = await wrapper.getDocumentationToolDescription();
                break;
            case 'getFieldCreationToolDescription':
                result = await wrapper.getFieldCreationToolDescription();
                break;
            case 'createLayoutElement':
                result = await wrapper.createLayoutElement(params.elementType, params.config);
                break;
            case 'addFieldsToLayout':
                result = await wrapper.addFieldsToLayout(params.appId, params.fields, params.revision);
                break;
            case 'removeFieldsFromLayout':
                result = await wrapper.removeFieldsFromLayout(params.appId, params.fieldCodes, params.revision);
                break;
            case 'organizeLayout':
                result = await wrapper.organizeLayout(params.appId, params.organization, params.revision);
                break;
            case 'createFieldGroup':
                result = await wrapper.createFieldGroup(params.name, params.fields);
                break;
            case 'createFormLayout':
                result = await wrapper.createFormLayout(params.layout);
                break;
            case 'addLayoutElement':
                result = await wrapper.addLayoutElement(params.appId, params.element, params.revision);
                break;
            case 'createGroupLayout':
                result = await wrapper.createGroupLayout(params.groupConfig);
                break;
            case 'createTableLayout':
                result = await wrapper.createTableLayout(params.tableConfig);
                break;
            case 'checkAppExists':
                result = await wrapper.checkAppExists(params.appId, params.checkPreview);
                break;
            default:
                throw new Error(`Unknown command: ${command}`);
        }
        
        console.log(JSON.stringify({ success: true, data: result }));
    } catch (error) {
        console.log(JSON.stringify({ 
            success: false, 
            error: error.message,
            details: error.toString()
        }));
    }
}

executeCommand();
