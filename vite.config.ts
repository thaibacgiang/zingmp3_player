
import {defineConfig} from "vite";

export default defineConfig({
    build:{
        lib:{
            entry:"src/card.ts",
            formats:["es"],
            fileName:()=>"zingmp3-media-card.js"
        },
        target:"es2022",
        minify:true
    }
});
