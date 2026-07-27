
import {LitElement,html,nothing} from "lit";

import {customElement,property,state} from "lit/decorators.js";

import {styles} from "./styles";

import {CARD_VERSION} from "./const";

@customElement("zingmp3-media-card")

export class ZingMP3Card extends LitElement{

static styles=styles;

@property({attribute:false})

public hass:any;

@state()

private config:any;

setConfig(config:any){

    if(!config.entity){

        throw new Error("Entity required");

    }

    this.config=config;

}

render(){

const state=this.hass.states[this.config.entity];

if(!state){

return html`

<ha-card>

Entity not found

</ha-card>

`;

}

const attr=state.attributes;

return html`

<ha-card>

<div class="header">

<img

class="cover"

src="${attr.entity_picture ?? ""}"

>

<div class="info">

<div class="title">

${attr.media_title ?? "Không phát"}

</div>

<div class="artist">

${attr.media_artist ?? ""}

</div>

</div>

</div>

<div class="controls">

<ha-icon-button

icon="mdi:skip-previous"

@click=${()=>this.hass.callService(

"media_player",

"media_previous_track",

{

entity_id:this.config.entity

}

)}

></ha-icon-button>

<ha-icon-button

icon="${state.state=="playing"

?"mdi:pause"

:"mdi:play"}"

@click=${()=>this.hass.callService(

"media_player",

"media_play_pause",

{

entity_id:this.config.entity

}

)}

></ha-icon-button>

<ha-icon-button

icon="mdi:skip-next"

@click=${()=>this.hass.callService(

"media_player",

"media_next_track",

{

entity_id:this.config.entity

}

)}

></ha-icon-button>

</div>

</ha-card>

`;

}

getCardSize(){

return 4;

}

static getStubConfig(){

return{

entity:"media_player.zingmp3"

};

}

}

console.info(

`ZingMP3 Card ${CARD_VERSION} loaded`

);
