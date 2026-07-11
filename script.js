// ========== 项目数据 ==========
const projects = [
    {
        name: '模拟校园证券交易所',
        desc: '模拟校园股票交易平台',
        web: 'https://racoldcn.github.io/XMStock/',
        repo: 'https://github.com/RacoldCN/XMStock'
    },
    {
        name: '张文见tm的鬼',
        desc: '张文名言录音',
        web: 'https://racoldcn.github.io/zhangwen/',
        repo: 'https://github.com/RacoldCN/zhangwen'
    },
    {
        name: '向明中学超科学社',
        desc: '向明中学超科学社社团宣传网站',
        web: 'https://racoldcn.github.io/HSC/',
        repo: 'https://github.com/RacoldCN/HSC'
    },
    {
        name: '吃掉小张文',
        desc: '基于开源仓库制作的张文老师版亚音游',
        web: 'https://racoldcn.github.io/EatSanxiao/',
        repo: 'https://github.com/RacoldCN/EatSanxiao'
    },
    {
        name: '模拟校园证券交易所原版',
        desc: '基于校园事件的股票模拟后端',
        web: null,
        repo: 'https://github.com/RacoldCN/stock'
    }
];

// ========== 渲染项目卡片 ==========
function renderProjects() {
    const grid = document.getElementById('projectsGrid');
    grid.innerHTML = projects.map(p => `
        <div class="project-card">
            <div class="project-info">
                <div class="project-name">${escapeHtml(p.name)}</div>
                <div class="project-desc">${escapeHtml(p.desc)}</div>
            </div>
            <div class="project-actions">
                ${p.web ? `
                    <a href="${escapeHtml(p.web)}" target="_blank" rel="noopener" class="btn btn-web">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                        网页
                    </a>
                ` : ''}
                ${p.repo ? `
                    <a href="${escapeHtml(p.repo)}" target="_blank" rel="noopener" class="btn btn-gh">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
                        仓库
                    </a>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ========== 每日习语 ==========
async function fetchDailyXiyu() {
    const loading = document.getElementById('xiyuLoading');
    const error = document.getElementById('xiyuError');
    const content = document.getElementById('xiyuContent');

    try {
        loading.style.display = 'block';
        error.style.display = 'none';
        content.style.display = 'none';

        // 添加时间戳参数防止缓存
        const resp = await fetch(`xiyu.json?t=${Date.now()}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        displayXiyu(data);
    } catch (e) {
        console.error('习语读取失败:', e);
        loading.style.display = 'none';
        error.textContent = '获取失败，请稍后刷新页面';
        error.style.display = 'block';
    }
}

function displayXiyu(data) {
    const loading = document.getElementById('xiyuLoading');
    const content = document.getElementById('xiyuContent');

    loading.style.display = 'none';
    content.style.display = 'block';

    document.getElementById('xiyuTitle').textContent = data.title;
    document.getElementById('xiyuBody').textContent = data.body;

    const now = new Date();
    const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    document.getElementById('xiyuTime').textContent = `更新于 ${timeStr}`;
}

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', () => {
    renderProjects();
    fetchDailyXiyu();
});
