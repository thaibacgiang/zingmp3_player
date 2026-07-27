
export const callPlayerService=(

    hass:any,

    service:string,

    data:any

)=>{

    return hass.callService(

        "zingmp3_player",

        service,

        data

    );

};
