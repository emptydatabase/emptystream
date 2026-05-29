const autoSkipped = new Set();
let activeSegIdx = -1;
let skipBtn = null;

document.addEventListener('DOMContentLoaded', () => {
    const segments = window.SB_SEGMENTS;
    if (!segments || !segments.length) return;

    skipBtn = document.createElement('button');
    skipBtn.className = 'sb-skip-btn hidden';
    skipBtn.textContent = 'Skip';
    const container = document.querySelector('.video-container');
    container.appendChild(skipBtn);

    const video = container.querySelector('video');
    video.addEventListener('timeupdate', () => {
        const t = video.currentTime;
        const idx = segments.findIndex(s => t >= s.start && t < s.end);

        if (idx === -1) {
            if (activeSegIdx !== -1) {
                activeSegIdx = -1;
                skipBtn.classList.add('hidden');
            }
            return;
        }

        const seg = segments[idx];
        if (seg.end > video.duration) return;

        const key = `${seg.start}-${seg.end}`;
        if (!autoSkipped.has(key)) {
            video.currentTime = seg.end;
            autoSkipped.add(key);
            skipBtn.classList.add('hidden');
            activeSegIdx = -1;
        } else {
            activeSegIdx = idx;
            skipBtn.textContent = `Skip ${seg.category}`;
            skipBtn.classList.remove('hidden');
            skipBtn.onclick = () => {
                video.currentTime = seg.end;
                skipBtn.classList.add('hidden');
                activeSegIdx = -1;
            };
        }
    });
});
