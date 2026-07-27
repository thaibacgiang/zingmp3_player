import {debounce} from "./helpers";

import * as api from "./api";

export default class SearchManager{

    private hass:any;

    constructor(hass:any){

        this.hass=hass;

    }

    public search=debounce(async(

        keyword:string

    )=>{

        return api.call(

            this.hass,

            "search",

            {

                keyword

            }

        );

    },400);

}
