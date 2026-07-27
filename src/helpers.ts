export function formatTime(sec: number): string {

    if (!sec || sec < 0) return "0:00";

    const m = Math.floor(sec / 60);

    const s = Math.floor(sec % 60);

    return `${m}:${String(s).padStart(2, "0")}`;

}

export function clamp(value: number, min: number, max: number): number {

    return Math.min(Math.max(value, min), max);

}

export function debounce<T extends (...args: any[]) => void>(
    fn: T,
    delay = 300
): T {

    let timer: number;

    return ((...args: any[]) => {

        clearTimeout(timer);

        timer = window.setTimeout(() => {

            fn(...args);

        }, delay);

    }) as T;

}

export function throttle<T extends (...args: any[]) => void>(
    fn: T,
    limit = 100
): T {

    let waiting = false;

    return ((...args: any[]) => {

        if (waiting) return;

        fn(...args);

        waiting = true;

        setTimeout(() => waiting = false, limit);

    }) as T;

}
