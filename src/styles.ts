
import {css} from "lit";

export const styles=css`

ha-card{

    overflow:hidden;

    border-radius:18px;

    padding:16px;

}

.header{

    display:flex;

    gap:16px;

}

.cover{

    width:110px;

    height:110px;

    border-radius:12px;

    object-fit:cover;

}

.info{

    flex:1;

}

.title{

    font-size:20px;

    font-weight:bold;

}

.artist{

    color:var(--secondary-text-color);

}

.controls{

    display:flex;

    justify-content:center;

    gap:18px;

    margin-top:20px;

}

`;
