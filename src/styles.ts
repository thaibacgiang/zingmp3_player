import {css} from "lit";

export const styles = css`

:host{

display:block;

}

ha-card{

position:relative;

overflow:hidden;

border-radius:18px;

padding:18px;

background:var(--ha-card-background,var(--card-background-color));

}

.background{

position:absolute;

inset:0;

background-size:cover;

background-position:center;

filter:blur(28px);

opacity:.25;

transform:scale(1.2);

pointer-events:none;

}

.content{

position:relative;

z-index:1;

}

.header{

display:flex;

gap:18px;

align-items:center;

}

.cover{

width:120px;

height:120px;

border-radius:14px;

object-fit:cover;

box-shadow:

0 10px 30px rgba(0,0,0,.35);

}

.info{

flex:1;

overflow:hidden;

}

.title{

font-size:22px;

font-weight:700;

white-space:nowrap;

overflow:hidden;

text-overflow:ellipsis;

}

.artist{

margin-top:6px;

font-size:15px;

color:var(--secondary-text-color);

white-space:nowrap;

overflow:hidden;

text-overflow:ellipsis;

}

.progress{

margin-top:22px;

}

.time{

display:flex;

justify-content:space-between;

font-size:12px;

color:var(--secondary-text-color);

margin-top:6px;

}

.controls{

display:flex;

justify-content:center;

align-items:center;

gap:22px;

margin-top:18px;

}

.play{

--mdc-icon-size:42px;

}

.volume{

margin-top:18px;

}

ha-slider{

width:100%;

}

@media(max-width:700px){

.header{

flex-direction:column;

text-align:center;

}

.cover{

width:170px;

height:170px;

}

}

`;
