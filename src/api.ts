export async function call(

    hass:any,

    service:string,

    data:any={}

){

    return hass.callService(

        "zingmp3_player",

        service,

        data

    );

}

export async function play(

    hass:any,

    song:string

){

    return call(

        hass,

        "play",

        {

            song

        }

    );

}

export async function pause(

    hass:any

){

    return call(

        hass,

        "pause"

    );

}

export async function next(

    hass:any

){

    return call(

        hass,

        "next"

    );

}

export async function previous(

    hass:any

){

    return call(

        hass,

        "previous"

    );

}

export async function volume(

    hass:any,

    value:number

){

    return hass.callService(

        "media_player",

        "volume_set",

        {

            entity_id:data.entity,

            volume_level:value

        }

    );

}

export async function seek(

    hass:any,

    entity:string,

    second:number

){

    return hass.callService(

        "media_player",

        "media_seek",

        {

            entity_id:entity,

            seek_position:second

        }

    );

}
