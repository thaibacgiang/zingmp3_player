export interface Song {

    id: string;

    title: string;

    artist: string;

    thumbnail: string;

    duration: number;

}

export interface Playlist {

    id: string;

    title: string;

    songs: Song[];

}

export interface CardConfig {

    entity: string;

    title?: string;

    artwork?: boolean;

    lyrics?: boolean;

    search?: boolean;

    playlist?: boolean;

}
