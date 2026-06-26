import { createApp, ref } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import axios from 'axios';

const App = {
  setup() {
    const username = ref('admin');
    const password = ref('');
    const token = ref(localStorage.getItem('token') || '');
    const status = ref<any>(null);
    const files = ref<any[]>([]);
    async function login() { const r = await axios.post('/api/auth/login', { username: username.value, password: password.value }); token.value = r.data.access_token; localStorage.setItem('token', token.value); await load(); }
    async function load() { const h = { Authorization: `Bearer ${token.value}` }; status.value = (await axios.get('/api/system/status', { headers: h })).data; files.value = (await axios.get('/api/files', { headers: h })).data; }
    if (token.value) load();
    return { username, password, token, status, files, login, load };
  },
  template: `<el-container><el-header><b>Telegram Archive Downloader Pro</b></el-header><el-main><el-card v-if="!token"><el-input v-model="username"/><el-input v-model="password" type="password"/><el-button type="primary" @click="login">Login</el-button></el-card><div v-else><el-row :gutter="12"><el-col :span="6" v-for="(v,k) in status" :key="k"><el-card><b>{{k}}</b><p>{{v}}</p></el-card></el-col></el-row><el-table :data="files"><el-table-column prop="filename" label="File"/><el-table-column prop="status" label="Status"/><el-table-column prop="downloaded_bytes" label="Bytes"/></el-table></div></el-main></el-container>`
};

createApp(App).use(ElementPlus).mount('#app');
