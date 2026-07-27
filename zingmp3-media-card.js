/**
 * Zing MP3 Media Card for Home Assistant
 * Version: 2026.2.9 (HA 2026.7+ compatible)
 * 
 * This file combines all necessary components for Zing MP3 player card
 * with fixes for compatibility with Home Assistant 2026.7+
 */

// ============================================
// UTILITY FUNCTIONS
// ============================================

const PlayableMediaList = ["track", "playlist", "tv_show", "album"];
const FetchableMediaContentType = [
    "vid_channel",
    "playlist",
    "track",
    "speakers",
    "music",
];

function secondsToMMSS(seconds) {
    if (seconds == undefined || seconds == null || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function isNumeric(num) {
    return (typeof num === "number" ||
        (typeof num === "string" && num.trim() !== "")) &&
        !isNaN(num);
}

function areDeeplyEqual(obj1, obj2, ignoreKeys = []) {
    if (obj1 === obj2) return true;
    if (Array.isArray(obj1) && Array.isArray(obj2)) {
        if (obj1.length !== obj2.length) return false;
        return obj1.every((elem, index) => {
            return areDeeplyEqual(elem, obj2[index], ignoreKeys);
        });
    }
    if (typeof obj1 === "object" &&
        typeof obj2 === "object" &&
        obj1 !== null &&
        obj2 !== null) {
        if (Array.isArray(obj1) || Array.isArray(obj2)) return false;
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);
        if (keys1.length !== keys2.length ||
            !keys1.every((key) => keys2.includes(key)))
            return false;
        for (let key in obj1) {
            if (ignoreKeys.includes(key)) continue;
            let isEqual = areDeeplyEqual(obj1[key], obj2[key], ignoreKeys);
            if (!isEqual) return false;
        }
        return true;
    }
    return false;
}

// ============================================
// ICONS
// ============================================

const ArrowLeftIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>arrow-left</title>
        <path
            d="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z" />
    </svg>
`;

const CastAudioIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path
            d="M2 11V13C7 13 11 17 11 22H13C13 15.9 8.1 11 2 11M20 2H10C8.9 2 8 2.9 8 4V10.5C9 11 9.9 11.7 10.7 12.4C11.6 11 13.2 10 15 10C17.8 10 20 12.2 20 15S17.8 20 15 20H14.8C14.9 20.7 15 21.3 15 22H20C21.1 22 22 21.1 22 20V4C22 2.9 21.1 2 20 2M15 8C13.9 8 13 7.1 13 6C13 4.9 13.9 4 15 4C16.1 4 17 4.9 17 6S16.1 8 15 8M15 18C14.8 18 14.5 18 14.3 17.9C13.8 16.4 13.1 15.1 12.2 13.9C12.6 12.8 13.7 11.9 15 11.9C16.7 11.9 18 13.2 18 14.9S16.7 18 15 18M2 15V17C4.8 17 7 19.2 7 22H9C9 18.1 5.9 15 2 15M2 19V22H5C5 20.3 3.7 19 2 19" />
    </svg>
`;

const CloseIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path
            d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
    </svg>
`;

const ForwardBurgerIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>forwardburger</title>
        <path
            d="M19,13H3V11H19L15,7L16.4,5.6L22.8,12L16.4,18.4L15,17L19,13M3,6H13V8H3V6M13,16V18H3V16H13Z" />
    </svg>
`;

const RadioTowerIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path
            d="M12,10A2,2 0 0,1 14,12C14,12.5 13.82,12.94 13.53,13.29L16.7,22H14.57L12,14.93L9.43,22H7.3L10.47,13.29C10.18,12.94 10,12.5 10,12A2,2 0 0,1 12,10M12,8A4,4 0 0,0 8,12C8,12.5 8.1,13 8.28,13.46L7.4,15.86C6.53,14.81 6,13.47 6,12A6,6 0 0,1 12,6A6,6 0 0,1 18,12C18,13.47 17.47,14.81 16.6,15.86L15.72,13.46C15.9,13 16,12.5 16,12A4,4 0 0,0 12,8M12,4A8,8 0 0,0 4,12C4,14.36 5,16.5 6.64,17.94L5.92,19.94C3.54,18.11 2,15.23 2,12A10,10 0 0,1 12,2A10,10 0 0,1 22,12C22,15.23 20.46,18.11 18.08,19.94L17.36,17.94C19,16.5 20,14.36 20,12A8,8 0 0,0 12,4Z" />
    </svg>
`;

const RepeatIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>repeat</title>
        <path
            d="M17,17H7V14L3,18L7,22V19H19V13H17M7,7H17V10L21,6L17,2V5H5V11H7V7Z" />
    </svg>
`;

const ShuffleVariantIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>shuffle-variant</title>
        <path
            d="M17,3L22.25,7.5L17,12L22.25,16.5L17,21V18H14.26L11.44,15.18L13.56,13.06L15.5,15H17V12L17,9H15.5L6.5,18H2V15H5.26L14.26,6H17V3M2,6H6.5L9.32,8.82L7.2,10.94L5.26,9H2V6Z" />
    </svg>
`;

const SkipNextIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>skip-next</title>
        <path d="M16,18H18V6H16M6,18L14.5,12L6,6V18Z" />
    </svg>
`;

const SkipPreviousIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>skip-previous</title>
        <path d="M6,18V6H8V18H6M9.5,12L18,6V18L9.5,12Z" />
    </svg>
`;

const PauseIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>pause</title>
        <path d="M14,19H18V5H14M6,19H10V5H6V19Z" />
    </svg>
`;

const PlayIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>play</title>
        <path d="M8,5.14V19.14L19,12.14L8,5.14Z" />
    </svg>
`;

const ThumbUpIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>thumb-up</title>
        <path
            d="M23,10C23,8.89 22.1,8 21,8H14.68L15.64,3.43C15.66,3.33 15.67,3.22 15.67,3.11C15.67,2.7 15.5,2.32 15.23,2.05L14.17,1L7.59,7.58C7.22,7.95 7,8.45 7,9V19A2,2 0 0,0 9,21H18C18.83,21 19.54,20.5 19.84,19.78L22.86,12.73C22.95,12.5 23,12.26 23,12V10M1,21H5V9H1V21Z" />
    </svg>
`;

const ThumbUpOutlineIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>thumb-up-outline</title>
        <path
            d="M5,9V21H1V9H5M9,21A2,2 0 0,1 7,19V9C7,8.45 7.22,7.95 7.59,7.59L14.17,1L15.23,2.06C15.5,2.33 15.67,2.7 15.67,3.11L15.64,3.43L14.69,8H21C22.11,8 23,8.9 23,10V12C23,12.26 22.95,12.5 22.86,12.73L19.84,19.78C19.54,20.5 18.83,21 18,21H9M9,19H18.03L21,12V10H12.21L13.34,4.68L9,9.03V19Z" />
    </svg>
`;

const VolumeHighIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>volume-high</title>
        <path
            d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12M3,9V15H7L12,20V4L7,9H3Z" />
    </svg>
`;

const VolumeOffIcon = html`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <title>volume-off</title>
        <path
            d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.53C15.58,18.04 14.83,18.46 14,18.7V20.77C15.38,20.45 16.63,19.82 17.68,18.96L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.82 18.46,14.64L19.97,16.15C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12C16.5,10.23 15.5,8.71 14,7.97V10.18L16.45,12.63C16.5,12.43 16.5,12.21 16.5,12Z" />
    </svg>
`;

// ============================================
// COMPONENT: PoLRYTubeListItem
// ============================================

class PoLRYTubeListItem extends LitElement {
    static get properties() {
        return {
            entity: { type: Object, state: true },
            hass: { type: Object, state: true },
            element: { type: Object, state: true },
            current: { type: Boolean, state: true },
        };
    }

    constructor() {
        super();
        this._actions = [];
        this._hasAdditionalActions = false;
        this._primaryAction = "play";
    }

    firstUpdated(_changedProperties) {
        if (this.element.can_expand) {
            this._primaryAction = "more";
        } else {
            this._primaryAction = "play";
        }
        this._hasAdditionalActions =
            this.element.can_expand == this.element.can_play
                ? this.element.can_expand
                : this.element.media_content_type == "track";
        this.requestUpdate();
    }

    render() {
        return html`
            <mwc-list-item
                graphic="medium"
                hasMeta
                @click=${this._performPrimaryAction}
                ?activated=${this.current}
            >
                ${this._renderThumbnail(this.element)} ${this.element.title}
                ${this._renderAction()}
            </mwc-list-item>
            ${this._hasAdditionalActions
                ? html`
                    <div class="divider"></div>
                    <div class="actions">
                        ${this._primaryAction != "more"
                            ? this._renderMoreButton(this.element)
                            : html``}
                        ${this._primaryAction != "play"
                            ? this._renderPlayButton(this.element)
                            : html``}
                        ${this._renderRadioButton(this.element)}
                    </div>
                `
                : html``}
        `;
    }

    _performPrimaryAction() {
        if (this._primaryAction == "more") {
            this._fireNavigateEvent(this.element);
        }
        if (this._primaryAction == "play") {
            this._play(this.element);
        }
    }

    _renderAction() {
        if (this._primaryAction == "more") {
            return html`<span slot="meta">${ForwardBurgerIcon}</span>`;
        }
        if (this._primaryAction == "play") {
            return html`<ha-icon slot="meta" icon="mdi:play"></ha-icon>`;
        }
        return html``;
    }

    _renderMoreButton(element) {
        if (!element["can_expand"]) return html``;
        return html`
            <mwc-icon-button @click=${() => this._fireNavigateEvent(element)}>
                ${ForwardBurgerIcon}
            </mwc-icon-button>
        `;
    }

    _renderPlayButton(element) {
        if (!element.can_play) return html``;
        return html`
            <mwc-icon-button @click=${() => this._play(element)}>
                ${PlayIcon}
            </mwc-icon-button>
        `;
    }

    _renderRadioButton(element) {
        if (element.media_content_type == "track") {
            const id = element.media_content_type == "track"
                ? element.media_content_id
                : this.entity?.attributes?.videoId;
            return html`
                <mwc-icon-button @click=${() => this._startRadio(id)}>
                    ${RadioTowerIcon}
                </mwc-icon-button>
            `;
        }
        return nothing;
    }

    _renderThumbnail(element) {
        if (element.thumbnail == "") {
            return html`<div slot="graphic" class="empty-thumbnail thumbnail">
                <ha-icon icon="mdi:music-box"></ha-icon>
            </div>`;
        }
        return html`
            <img slot="graphic" class="thumbnail" src="${element.thumbnail}" />
        `;
    }

    async _fireNavigateEvent(element) {
        this.dispatchEvent(new CustomEvent("navigate", {
            detail: {
                action: element,
            },
        }));
        return;
    }

    async _startRadio(media_content_id) {
        await this._callService("media_player", "shuffle_set", {
            entity_id: this.entity.entity_id,
            shuffle: false,
        });
        await this._callService("media_player", "play_media", {
            entity_id: this.entity.entity_id,
            media_content_id: media_content_id,
            media_content_type: "vid_channel",
        });
        return;
    }

    async _play(element) {
        if (element.media_content_type == "PLAYLIST_GOTO_TRACK") {
            await this._callService("zingmp3_player", "call_method", {
                entity_id: this.entity.entity_id,
                command: "goto_track",
                parameters: element.media_content_id,
            });
            return;
        }
        if (PlayableMediaList.includes(element.media_class)) {
            await this._callService("media_player", "play_media", {
                entity_id: this.entity.entity_id,
                media_content_id: element.media_content_id,
                media_content_type: element.media_content_type,
            });
            return;
        }
    }

    async _callService(domain, service, data) {
        try {
            if (!this.hass) {
                console.error('No hass instance available');
                return;
            }
            return await this.hass.callService(domain, service, data);
        } catch (e) {
            console.error(`Error calling ${domain}.${service}:`, e);
            throw e;
        }
    }

    static get styles() {
        return [
            css`
                :host {
                    display: grid;
                    grid-template-columns: 1fr min-content min-content;
                    align-items: center;
                }

                mwc-list-item {
                    border-radius: 12px;
                }

                svg {
                    width: 18px;
                    height: 18px;
                    fill: var(--primary-text-color);
                }

                .divider {
                    width: 2px;
                    background: rgba(var(--rgb-primary-text-color), 0.2);
                    height: 50%;
                    margin: 0 4px;
                }

                .actions {
                    display: grid;
                    grid-template-columns: auto;
                    align-items: center;
                }

                .actions > mwc-button {
                    margin: 0 8px;
                }

                .element img {
                    width: 40px;
                    height: 40px;
                    border-radius: 5%;
                }

                .empty-thumbnail {
                    display: flex;
                    background-color: rgba(111, 111, 111, 0.2);
                    border-radius: 5%;
                    height: 40px;
                    align-items: center;
                    justify-content: center;
                }
            `,
        ];
    }
}
customElements.define("zingmp3-list-item", PoLRYTubeListItem);

// ============================================
// COMPONENT: PoLRYTubeGridItem
// ============================================

class PoLRYTubeGridItem extends LitElement {
    static get properties() {
        return {
            entity: { type: Object, state: true },
            hass: { type: Object, state: true },
            element: { type: Object, state: true },
            current: { type: Boolean, state: true },
        };
    }

    constructor() {
        super();
        this._actions = [];
        this._hasAdditionalActions = false;
        this._primaryAction = "play";
    }

    firstUpdated(_changedProperties) {
        if (this.element.can_expand) {
            this._primaryAction = "more";
        } else {
            this._primaryAction = "play";
        }
        this._hasAdditionalActions =
            this.element.can_expand == this.element.can_play
                ? this.element.can_expand
                : this.element.media_content_type == "track";
        this.requestUpdate();
    }

    render() {
        return html`
            <div class="grid-item" @click=${this._performPrimaryAction}>
                <div>${this._renderThumbnail(this.element)}</div>
                <span class="title"> ${this.element.title}</span>
                <div class="actions">
                    ${this._hasAdditionalActions
                        ? html`
                            ${this._primaryAction != "more"
                                ? this._renderMoreButton(this.element)
                                : html``}
                            ${this._primaryAction != "play"
                                ? this._renderPlayButton(this.element)
                                : html``}
                            ${this._renderRadioButton(this.element)}
                        `
                        : html``}
                </div>
            </div>
        `;
    }

    _performPrimaryAction() {
        if (this._primaryAction == "more") {
            this._fireNavigateEvent(this.element);
        }
        if (this._primaryAction == "play") {
            this._play(this.element);
        }
    }

    _renderPrimaryAction() {
        if (this._primaryAction == "more") {
            return this._renderMoreButton(this.element);
        }
        if (this._primaryAction == "play") {
            return this._renderPlayButton(this.element);
        }
        return html``;
    }

    _renderMoreButton(element) {
        if (!element["can_expand"]) return html``;
        return html`
            <mwc-icon-button @click=${() => this._fireNavigateEvent(element)}>
                ${ForwardBurgerIcon}
            </mwc-icon-button>
        `;
    }

    _renderPlayButton(element) {
        if (!element.can_play) return html``;
        return html`
            <mwc-icon-button @click=${() => this._play(element)}>
                ${PlayIcon}
            </mwc-icon-button>
        `;
    }

    _renderRadioButton(element) {
        if (element.media_content_type == "track") {
            const id = element.media_content_type == "track"
                ? element.media_content_id
                : this.entity?.attributes?.videoId;
            return html`
                <mwc-icon-button @click=${() => this._startRadio(id)}>
                    ${RadioTowerIcon}
                </mwc-icon-button>
            `;
        }
        return nothing;
    }

    _renderThumbnail(element) {
        if (element.thumbnail == "") {
            return html`<div class="empty-thumbnail thumbnail">
                <ha-icon icon="mdi:music-box"></ha-icon>
            </div>`;
        }
        return html` <img class="thumbnail" src="${element.thumbnail}" /> `;
    }

    async _fireNavigateEvent(element) {
        this.dispatchEvent(new CustomEvent("navigate", {
            detail: {
                action: element,
            },
        }));
        return;
    }

    async _startRadio(media_content_id) {
        await this._callService("media_player", "shuffle_set", {
            entity_id: this.entity.entity_id,
            shuffle: false,
        });
        await this._callService("media_player", "play_media", {
            entity_id: this.entity.entity_id,
            media_content_id: media_content_id,
            media_content_type: "vid_channel",
        });
        return;
    }

    async _play(element) {
        if (element.media_content_type == "PLAYLIST_GOTO_TRACK") {
            await this._callService("zingmp3_player", "call_method", {
                entity_id: this.entity.entity_id,
                command: "goto_track",
                parameters: element.media_content_id,
            });
            return;
        }
        if (PlayableMediaList.includes(element.media_class)) {
            await this._callService("media_player", "play_media", {
                entity_id: this.entity.entity_id,
                media_content_id: element.media_content_id,
                media_content_type: element.media_content_type,
            });
            return;
        }
    }

    async _callService(domain, service, data) {
        try {
            if (!this.hass) {
                console.error('No hass instance available');
                return;
            }
            return await this.hass.callService(domain, service, data);
        } catch (e) {
            console.error(`Error calling ${domain}.${service}:`, e);
            throw e;
        }
    }

    static get styles() {
        return [
            css`
                :host {
                }

                .grid-item {
                    position: relative;
                    display: grid;
                    aspect-ratio: 1 / 1;
                    cursor: pointer;
                    border-radius: 5px;
                    overflow: hidden;
                }

                .grid-item:focus {
                    outline: dotted thin;
                }

                .title {
                    position: absolute;
                    z-index: 2;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    padding: 4px 8px;
                    background-color: color-mix(
                        in srgb,
                        var(--primary-color) 50%,
                        #000000aa
                    );
                    font-size: 12px;
                    overflow: hidden;
                    display: -webkit-box;
                    -webkit-box-orient: vertical;
                    -webkit-line-clamp: 2;
                    color: #ffffff;
                }

                .actions {
                    position: absolute;
                    display: grid;
                    align-items: center;
                    grid-template-columns: auto;
                    top: 4px;
                    right: 4px;
                    background: rgba(0, 0, 0, 0.25);
                    border-radius: 9999px;
                }

                .actions > mwc-button {
                    margin: 0 8px;
                }

                .thumbnail {
                    width: 100%;
                    height: 100%;
                }

                .empty-thumbnail {
                    display: flex;
                    background-color: rgba(111, 111, 111, 0.2);
                    align-items: center;
                    justify-content: center;
                }
            `,
        ];
    }
}
customElements.define("zingmp3-grid-item", PoLRYTubeGridItem);

// ============================================
// COMPONENT: PoLRYTubeList
// ============================================

class PoLRYTubeList extends LitElement {
    static get properties() {
        return {
            entity: { type: Object, state: true },
            hass: { type: Object, state: true },
            elements: { type: Array, state: true },
            state: { type: Number, state: true },
            columns: { type: Number },
            grid: { type: Boolean },
        };
    }

    constructor() {
        super();
        this.columns = 1;
        this.grid = false;
        this.elements = [];
        this.state = 4; // LOADING
        this.entity = null;
        this.hass = null;
    }

    render() {
        if (this.state == 4) {
            return html`<div class="loading">Loading...</div>`;
        }
        if (this.state == 8) {
            return html`<div class="empty">No results</div>`;
        }
        if (this.state == 16) {
            return html`<div class="error">Unknown Error</div>`;
        }
        if (this.state == 2) {
            if (this.elements.length == 0) return html``;
            let renderedElements;
            if (this.grid) {
                renderedElements = this.elements.map((element) => {
                    return html`
                        <zingmp3-grid-item
                            .hass=${this.hass}
                            .entity=${this.entity}
                            .element=${element}
                            .current=${this._is_current(element)}
                            @navigate=${(ev) => this._fireNavigateEvent(ev.detail.action)}
                        ></zingmp3-grid-item>
                    `;
                });
            } else {
                renderedElements = this.elements.map((element) => {
                    return html`
                        <zingmp3-list-item
                            .hass=${this.hass}
                            .entity=${this.entity}
                            .element=${element}
                            .current=${this._is_current(element)}
                            @navigate=${(ev) => this._fireNavigateEvent(ev.detail.action)}
                        ></zingmp3-list-item>
                    `;
                });
            }
            return html`
                <div
                    class="container"
                    style="--zingmp3-list-columns: ${this.columns}"
                >
                    ${renderedElements}
                </div>
            `;
        }
        return html``;
    }

    _is_current(element) {
        if (this.entity == null) return false;
        if (!isNumeric(element.media_content_id)) return false;
        const attrs = this.entity.attributes || {};
        if ("current_track" in attrs) {
            return (parseInt(element.media_content_id) - 1 ==
                attrs.current_track);
        }
        return false;
    }

    async _fireNavigateEvent(element) {
        this.dispatchEvent(new CustomEvent("navigate", {
            detail: {
                action: element,
            },
        }));
        return;
    }

    static get styles() {
        return [
            css`
                .container {
                    display: grid;
                    grid-template-columns: repeat(
                        var(--zingmp3-list-columns, 1),
                        minmax(0, 1fr)
                    );
                    gap: 8px;
                    --mdc-list-item-graphic-size: 40px;
                }

                .empty,
                .loading,
                .error {
                    display: grid;
                    align-items: center;
                    justify-items: center;
                    height: 100px;
                }
            `,
        ];
    }
}
customElements.define("zingmp3-list", PoLRYTubeList);

// ============================================
// COMPONENT: PoLRYTubeBrowser
// ============================================

class PoLRYTubeBrowser extends LitElement {
    static get properties() {
        return {
            entity: { type: Object, state: true },
            hass: { type: Object, state: true },
            initialAction: { type: Object },
            coverNavigation: { type: Boolean },
            initialElements: { type: Array, state: true },
        };
    }

    constructor() {
        super();
        this._browseHistory = [];
        this._previousBrowseHistory = [];
        this._isSearchResults = false;
        this.coverNavigation = false;
        this.initialElements = [];
    }

    updated(_changedProperties) {
        if (_changedProperties.has("initialAction")) {
            this._browseHistory = [];
            this._previousBrowseHistory = [];
            this._browse(this.initialAction);
        }
    }

    firstUpdated(_changedProperties) {
        this._polrYTubeList = this.renderRoot.querySelector("zingmp3-list");
        this._searchTextField = this.renderRoot.querySelector("#query");
    }

    render() {
        return html`
            <div class="container">
                ${this._renderSearch()} ${this._renderNavigation()}
                ${this._renderPlay()}
                <zingmp3-list
                    .hass=${this.hass}
                    .entity=${this.entity}
                    @navigate=${(ev) => this._browse(ev.detail.action)}
                    .grid=${this.coverNavigation}
                    columns=${this.coverNavigation ? "3" : "1"}
                ></zingmp3-list>
            </div>
        `;
    }

    _renderSearch() {
        return html`
            <div class="search">
                <polr-textfield
                    type="search"
                    id="query"
                    icon
                    @keyup="${this._handleSearchInput}"
                >
                    <ha-icon slot="icon" icon="mdi:magnify"></ha-icon>
                </polr-textfield>

                <polr-select
                    id="filter"
                    fixedMenuPosition
                    naturalMenuWidth
                    @selected=${this._search}
                >
                    <mwc-list-item value="all"> All </mwc-list-item>
                    <mwc-list-item value="artists"> Artists </mwc-list-item>
                    <mwc-list-item selected value="songs">
                        Songs
                    </mwc-list-item>
                    <mwc-list-item selected value="playlists">
                        Playlists
                    </mwc-list-item>
                </polr-select>
            </div>
        `;
    }

    loadElement(element) {
        this._browseHistory = [];
        this._browse(element);
    }

    async _browse(element) {
        this._polrYTubeList.state = 4;
        this._browseHistory.push(element);
        if (element?.children?.length > 0) {
            this._polrYTubeList.elements = element.children;
            this._polrYTubeList.state = 2;
        } else {
            try {
                const response = await this._browseMedia(
                    element.media_content_type,
                    element.media_content_id
                );
                if (response?.children) {
                    this._polrYTubeList.elements = response.children;
                    this._polrYTubeList.state = 2;
                } else {
                    this._polrYTubeList.state = 8;
                }
            } catch (e) {
                this._polrYTubeList.state = 16;
                console.error(e, element.media_content_type, element.media_content_id);
            }
        }
        this.requestUpdate();
    }

    async _browseMedia(contentType, contentId) {
        try {
            return await this.hass.callWS({
                type: 'media_player/browse_media',
                entity_id: this.entity?.entity_id,
                media_content_type: contentType,
                media_content_id: contentId || '',
            });
        } catch (e) {
            console.error('Browse media error:', e);
            return null;
        }
    }

    async _fetchSearchResults() {
        this._polrYTubeList.state = 4;
        try {
            let response = await this._browseMedia("search", "");
            if (response?.children?.length > 0) {
                response.children.filter((el) => !el.media_content_id?.startsWith("MPSP"));
                if (!this._isSearchResults) {
                    this._previousBrowseHistory = this._browseHistory;
                }
                this._isSearchResults = true;
                this._browseHistory = [];
                this._browse(response);
                this.requestUpdate();
            } else {
                this._polrYTubeList.state = 8;
            }
        } catch (e) {
            this._polrYTubeList.state = 16;
            console.error(e);
        }
    }

    _renderNavigation() {
        if (this._browseHistory.length <= 1 && !this._isSearchResults) {
            return html``;
        }
        let breadcrumbItems;
        if (this._browseHistory.length > 2) {
            breadcrumbItems = [
                this._browseHistory[0].title,
                "...",
                this._browseHistory[this._browseHistory.length - 1].title,
            ];
        } else {
            breadcrumbItems = this._browseHistory.map((item) => item.title);
        }
        let breadcrumb = html`
            ${this._renderBreadcrumb(breadcrumbItems)}
        `;
        return html`
            <div class="navigation-row">
                ${this._isSearchResults
                    ? html`
                        <mwc-icon-button
                            @click=${() => {
                                this._isSearchResults = false;
                                this._browseHistory =
                                    this._previousBrowseHistory;
                                this._searchTextField.value = "";
                                this._browse(this._browseHistory.pop());
                            }}
                        >
                            ${CloseIcon}
                        </mwc-icon-button>
                    `
                    : nothing}
                ${this._browseHistory.length > 1
                    ? html`
                        <mwc-icon-button
                            @click=${() => this._browse(this._browseHistory.pop() &&
                                this._browseHistory.pop())}
                        >
                            ${ArrowLeftIcon}
                        </mwc-icon-button>
                    `
                    : nothing}
                ${this._browseHistory.length > 1 || this._isSearchResults
                    ? html` <div class="breadcrumb">${breadcrumb}</div> `
                    : nothing}
            </div>
        `;
    }

    _renderBreadcrumb(items) {
        return html`
            ${items.map((item, index) => html`
                <span class="crumb">${item}</span>
                ${index < items.length - 1 ? html`<span class="separator">/</span>` : ''}
            `)}
        `;
    }

    _renderPlay() {
        const element = this._browseHistory[this._browseHistory.length - 1];
        if (element?.can_play) {
            return html`
                <div class="playable_result">
                    ${element.title}
                    <mwc-button
                        raised
                        dense
                        @click=${() => this._callService("media_player", "play_media", {
                            entity_id: this.entity.entity_id,
                            media_content_id: element.media_content_id,
                            media_content_type: element.media_content_type,
                        })}
                    >
                        Play
                    </mwc-button>
                </div>
            `;
        }
        return html``;
    }

    async _callService(domain, service, data) {
        try {
            if (!this.hass) {
                console.error('No hass instance available');
                return;
            }
            return await this.hass.callService(domain, service, data);
        } catch (e) {
            console.error(`Error calling ${domain}.${service}:`, e);
            throw e;
        }
    }

    _handleSearchInput(ev) {
        if (ev.keyCode == 13) {
            this._search();
            this._searchTextField?.blur();
        }
    }

    async _search() {
        const query = this.shadowRoot?.querySelector("#query")?.value;
        if (!query || query.trim() === '') return;
        
        const filter = this.renderRoot?.querySelector("#filter")?.selected?.value || 'songs';
        const entityId = this.entity?.entity_id;
        if (!entityId) return;
        
        let data = {
            entity_id: entityId,
            query: query,
            limit: 40,
        };
        if (filter !== "all") {
            data.filter = filter;
        }
        
        await this._callService("zingmp3_player", "search", data);
        this._fetchSearchResults();
    }

    static get styles() {
        return [
            css`
                .container {
                    display: flex;
                    overflow: auto;
                    flex-grow: 1;
                    flex-direction: column;
                    gap: 8px;
                }

                .navigation-row {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    justify-content: flex-start;
                    --mdc-icon-button-size: 30px;
                    --mdc-icon-size: 20px;
                }

                .breadcrumb {
                    display: flex;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    align-items: center;
                    margin-left: 4px;
                }

                .crumb {
                    background-color: rgba(111, 111, 111, 0.2);
                    padding: 4px 8px;
                    border-radius: 4px;
                    text-transform: uppercase;
                    font-size: 10px;
                    font-weight: bold;
                }

                .separator {
                    font-weight: bold;
                    padding: 4px;
                }

                .search {
                    display: grid;
                    grid-template-columns: 1fr 120px;
                    align-items: center;
                    gap: 4px;
                }

                .playable_result {
                    display: inline-flex;
                    justify-content: space-between;
                    align-items: center;
                }

                zingmp3-list {
                    overflow: auto;
                }

                #filter {
                    --select-height: 42px;
                    width: 100%;
                }

                #query {
                    --textfield-height: 42px;
                }
            `,
        ];
    }
}
customElements.define("zingmp3-browser", PoLRYTubeBrowser);

// ============================================
// COMPONENT: PoLRMediaControl
// ============================================

class PoLRMediaControl extends LitElement {
    static get properties() {
        return {
            hass: { type: Object },
            entity: { type: Object },
            progressTime: { type: String },
        };
    }

    constructor() {
        super();
        this.progressTime = "0:00";
        this.tracker = null;
        this.progressSlider = null;
        this.volumeSlider = null;
        this.volumeButton = null;
        this.volumeMenu = null;
    }

    async connectedCallback() {
        super.connectedCallback();
        this._trackProgress();
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        if (this.tracker) {
            clearInterval(this.tracker);
            this.tracker = null;
        }
    }

    firstUpdated(_changedProperties) {
        this.volumeSlider = this.renderRoot.querySelector("#volume");
        if (this.volumeSlider) {
            const attrs = this.entity?.attributes || {};
            this.volumeSlider.value = (attrs.volume_level || 0) * 100;
        }
        this.progressSlider = this.renderRoot.querySelector("#progressSlider");
        this.volumeButton = this.renderRoot.querySelector("#volumeButton");
        this.volumeMenu = this.renderRoot.querySelector("#volumeMenu");
    }

    render() {
        return html`
            <div class="action-row">
                ${this._renderVolume()} ${this._renderLikeButton()}
                ${this._renderRadioButton()}
            </div>
            <div class="progress-row">${this._renderProgress()}</div>
            <div class="control-row">
                ${this._renderShuffle()} ${this._renderPrevious()}
                ${this._renderPlayPause()} ${this._renderNext()}
                ${this._renderRepeat()}
            </div>
        `;
    }

    _renderLikeButton() {
        const attrs = this.entity?.attributes || {};
        if (!("likeStatus" in attrs)) return html``;
        const isLiked = attrs.likeStatus == "LIKE";
        return html`
            <mwc-icon-button @click=${() => this._likeSong()}>
                ${isLiked ? ThumbUpIcon : ThumbUpOutlineIcon}
            </mwc-icon-button>
        `;
    }

    _renderNext() {
        return html`
            <mwc-icon-button @click=${this._skipNext}>
                ${SkipNextIcon}
            </mwc-icon-button>
        `;
    }

    _renderPlayPause() {
        const isPlaying = this.entity?.state == "playing";
        return html`
            <mwc-icon-button class="playPause" @click=${this._togglePlayPause}>
                ${isPlaying ? PauseIcon : PlayIcon}
            </mwc-icon-button>
        `;
    }

    _renderPrevious() {
        return html`
            <mwc-icon-button @click=${this._skipPrevious}>
                ${SkipPreviousIcon}
            </mwc-icon-button>
        `;
    }

    _renderProgress() {
        const attrs = this.entity?.attributes || {};
        const duration = attrs.media_duration || 0;
        const totalTime = secondsToMMSS(duration);
        const current = attrs.media_position || 0;
        
        if (this.progressSlider && duration > 0) {
            this.progressSlider.max = Math.round(duration);
            this.progressSlider.value = Math.round(Math.min(current, duration));
        }
        
        return html`
            <div class="time">
                <span>${this.progressTime}</span>
                <polr-slider
                    id="progressSlider"
                    min="0"
                    step="1"
                    max="${Math.round(duration)}"
                    @change=${this._seekProgress}
                ></polr-slider>
                <span>${totalTime}</span>
            </div>
        `;
    }

    _renderRadioButton() {
        return html`
            <mwc-icon-button @click=${this._startRadio}>
                ${RadioTowerIcon}
            </mwc-icon-button>
        `;
    }

    _renderRepeat() {
        return html`
            <mwc-icon-button @click=${this._changeRepeat}>
                ${RepeatIcon}
            </mwc-icon-button>
        `;
    }

    _renderShuffle() {
        return html`
            <mwc-icon-button @click=${this._shuffleList}>
                ${ShuffleVariantIcon}
            </mwc-icon-button>
        `;
    }

    _renderVolume() {
        const attrs = this.entity?.attributes || {};
        const isMuted = attrs.is_volume_muted || false;
        return html`
            <div class="volumeMenuItems">
                <mwc-icon-button
                    id="volumeButton"
                    @click=${() => this.volumeMenu?.show()}
                >
                    ${isMuted ? VolumeOffIcon : VolumeHighIcon}
                </mwc-icon-button>
                <mwc-menu
                    id="volumeMenu"
                    .anchor=${this.volumeButton}
                    corner="BOTTOM_START"
                    menuCorner="START"
                    naturalmenuwidth
                    fixed
                >
                    <div class="volumeMenuItems">
                        <mwc-icon-button @click=${this._toggleMute}>
                            ${isMuted ? VolumeOffIcon : VolumeHighIcon}
                        </mwc-icon-button>
                        <polr-slider
                            id="volume"
                            min="0"
                            max="100"
                            steps="1"
                            @change=${this._changeVolume}
                        ></polr-slider>
                    </div>
                </mwc-menu>
            </div>
        `;
    }

    async _changeRepeat() {
        const attrs = this.entity?.attributes || {};
        const repeat = attrs.repeat || "off";
        let newRepeat;
        switch (repeat) {
            case "off":
                newRepeat = "one";
                break;
            case "one":
                newRepeat = "all";
                break;
            case "all":
                newRepeat = "off";
                break;
            default:
                newRepeat = "off";
        }
        await this._callService("media_player", "repeat_set", {
            entity_id: this.entity.entity_id,
            repeat: newRepeat,
        });
    }

    async _changeVolume() {
        const value = this.volumeSlider?.value || 0;
        await this._callService("media_player", "volume_set", {
            entity_id: this.entity.entity_id,
            volume_level: value / 100,
        });
    }

    async _likeSong() {
        await this._callService("zingmp3_player", "rate_track", {
            entity_id: this.entity?.entity_id,
            rating: "thumb_toggle_up_middle",
        });
        this.requestUpdate();
    }

    async _seekProgress() {
        const progress = this.progressSlider?.value || 0;
        await this._callService("media_player", "media_seek", {
            entity_id: this.entity.entity_id,
            seek_position: progress,
        });
    }

    async _shuffleList() {
        const attrs = this.entity?.attributes || {};
        const shuffle = attrs.shuffle || false;
        await this._callService("media_player", "shuffle_set", {
            entity_id: this.entity.entity_id,
            shuffle: !shuffle,
        });
    }

    async _skipNext() {
        await this._callService("media_player", "media_next_track", {
            entity_id: this.entity.entity_id,
        });
    }

    async _startRadio() {
        const attrs = this.entity?.attributes || {};
        await this._callService("media_player", "shuffle_set", {
            entity_id: this.entity.entity_id,
            shuffle: false,
        });
        await this._callService("media_player", "play_media", {
            entity_id: this.entity.entity_id,
            media_content_id: attrs.videoId,
            media_content_type: "vid_channel",
        });
    }

    async _toggleMute() {
        const attrs = this.entity?.attributes || {};
        await this._callService("media_player", "volume_mute", {
            entity_id: this.entity.entity_id,
            is_volume_muted: !attrs.is_volume_muted,
        });
    }

    async _trackProgress() {
        if (!this.entity) return;
        
        const attrs = this.entity.attributes || {};
        const now = Date.now();
        const updatedAt = attrs.media_position_updated_at;
        let position = attrs.media_position || 0;
        const duration = attrs.media_duration || 0;
        
        if (updatedAt && this.entity.state === "playing") {
            const lastUpdate = Date.parse(updatedAt);
            if (!isNaN(lastUpdate)) {
                position += (now - lastUpdate) / 1000;
            }
        }
        
        position = Math.min(position, duration);
        this.progressTime = secondsToMMSS(position);
        
        if (this.progressSlider && duration > 0) {
            this.progressSlider.value = Math.round(position);
            this.progressSlider.max = Math.round(duration);
        }
        
        if (!this.tracker) {
            this.tracker = setInterval(() => this._trackProgress(), 1000);
        }
    }

    async _skipPrevious() {
        await this._callService("media_player", "media_previous_track", {
            entity_id: this.entity.entity_id,
        });
    }

    async _togglePlayPause() {
        await this._callService("media_player", "media_play_pause", {
            entity_id: this.entity.entity_id,
        });
    }

    async _callService(domain, service, data) {
        try {
            if (!this.hass) {
                console.error('No hass instance available');
                return;
            }
            return await this.hass.callService(domain, service, data);
        } catch (e) {
            console.error(`Error calling ${domain}.${service}:`, e);
            throw e;
        }
    }

    static get styles() {
        return [
            css`
                :host {
                    display: grid;
                    gap: 4px;
                }

                .action-row {
                    display: grid;
                    grid-template-columns: min-content min-content min-content;
                    justify-content: space-evenly;
                }

                .progress-row {
                    display: grid;
                    grid-template-columns: 1fr;
                }

                .control-row {
                    display: grid;
                    grid-template-columns: min-content min-content min-content min-content min-content;
                    align-items: center;
                    justify-content: space-evenly;
                }

                .playPause {
                    --mdc-icon-button-size: 64px;
                    --mdc-icon-size: 48px;
                }
                
                .time {
                    display: grid;
                    grid-template-columns: min-content 1fr min-content;
                    align-items: center;
                }

                #volume {
                    --md-sys-color-primary: var(--primary-color);
                    --md-slider-handle-height: 10px;
                    --md-slider-handle-shape: 9999px;
                    --md-slider-active-track-shape: 9999px;
                    --md-slider-inactive-track-shape: 4px;
                    --md-slider-active-track-height: 5px;
                    --md-slider-inactive-track-height: 5px;
                }

                #progressSlider {
                    --md-sys-color-primary: var(--primary-color);
                    --md-slider-active-track-shape: 4px;
                    --md-slider-inactive-track-shape: 4px;
                }

                .volumeMenuItems {
                    display: grid;
                    grid-template-columns: min-content 1fr;
                    align-items: center;
                    padding: 0 12px;
                }
            `,
        ];
    }
}
customElements.define("polr-media-control", PoLRMediaControl);

// ============================================
// COMPONENT: PoLRYTubePlaying
// ============================================

class PoLRYTubePlaying extends LitElement {
    static get properties() {
        return {
            _hass: { type: Object, state: true },
            _entity: { type: Object, state: true },
        };
    }

    constructor() {
        super();
        this._hass = null;
        this._entity = null;
        this._polrYTubeList = null;
    }

    firstUpdated(_changedProperties) {
        this._polrYTubeList = this.renderRoot.querySelector("zingmp3-list");
        this._getCurrentlyPlayingItems();
    }

    render() {
        return html`
            <zingmp3-list
                .hass=${this._hass}
                .entity=${this._entity}
            ></zingmp3-list>
        `;
    }

    async _getCurrentlyPlayingItems() {
        if (!this._entity || this._entity.state == "idle") return;
        
        const attrs = this._entity.attributes || {};
        const mediaContentType = attrs.media_content_type;
        const mediaType = attrs._media_type;
        let results = {};
        
        try {
            if (FetchableMediaContentType.includes(mediaContentType) &&
                !["album"].includes(mediaType)) {
                results = await this._browseMedia("cur_playlists", "");
            }
            
            if (["album"].includes(mediaType)) {
                results = await this._browseMedia("album_of_track", "1");
                results?.children?.map((r, index) => {
                    r.media_content_type = "PLAYLIST_GOTO_TRACK";
                    r.media_content_id = index + 1;
                    return r;
                });
            }
            
            if (attrs.media_title == "loading...") {
                this._polrYTubeList.state = 4;
                return;
            }
            
            if (results?.children?.length > 0) {
                this._polrYTubeList.elements = results.children;
                this._polrYTubeList.state = 2;
            } else {
                this._polrYTubeList.state = 8;
            }
            this.requestUpdate();
        } catch (e) {
            console.error(e);
            this._polrYTubeList.state = 16;
        }
    }

    async _browseMedia(contentType, contentId) {
        try {
            if (!this._hass) return null;
            return await this._hass.callWS({
                type: 'media_player/browse_media',
                entity_id: this._entity?.entity_id,
                media_content_type: contentType,
                media_content_id: contentId || '',
            });
        } catch (e) {
            console.error('Browse media error:', e);
            return null;
        }
    }

    refresh(entity) {
        if (entity != null) this._entity = entity;
        this._getCurrentlyPlayingItems();
    }
}
customElements.define("zingmp3-playing", PoLRYTubePlaying);

// ============================================
// COMPONENT: PoLRYTubePlayingCard (MAIN CARD)
// ============================================

class PoLRYTubePlayingCard extends LitElement {
    static get properties() {
        return {
            _config: { type: Object },
            _hass: { type: Object },
            _entity: { type: Object, state: true },
            _activeTab: { type: Number, state: true },
        };
    }

    constructor() {
        super();
        this._config = {};
        this._activeTab = 0; // CURRENTLY_PLAYING
        this._entity = null;
        this._hass = null;
        this._sourceSelectorButton = null;
        this._sourceSelectorMenu = null;
        this._playing = null;
    }

    firstUpdated(_changedProperties) {
        this._sourceSelectorButton = this.renderRoot.querySelector("#sourceSelectorButton");
        this._sourceSelectorMenu = this.renderRoot.querySelector("#sourceSelectorMenu");
        this._playing = this.renderRoot.querySelector("#playing");
    }

    static getConfigElement() {
        return null;
    }

    static getStubConfig() {
        return {
            entity_id: "media_player.zingmp3_player",
            header: "Zing Mp3 Music",
        };
    }

    setConfig(config) {
        if (!config.entity_id) {
            throw new Error("entity_id must be specified");
        }
        this._config = structuredClone(config);
        if (!("header" in this._config)) {
            this._config.header = "Zing Mp3 Music";
        }
        if (!("icon" in this._config)) {
            this._config.icon = "mdi:speaker";
        }
        if (!("initialAction" in this._config)) {
            this._config.initialAction = {
                title: "You",
                media_content_type: null,
                media_content_id: null,
                can_expand: true,
                can_play: false,
                children: [],
            };
        }
        if (!("coverNavigation" in this._config)) {
            this._config.coverNavigation = false;
        }
    }

    set hass(hass) {
        this._hass = hass;
        const newEntity = this._hass?.states?.[this._config?.entity_id];
        if (!areDeeplyEqual(this._entity, newEntity, [])) {
            const oldState = this._entity?.state;
            if (oldState == "off" && newEntity?.state != "off") {
                this._changeTab(0);
            }
            this._entity = structuredClone(newEntity);
            if (this._entity?.state == "off") {
                this._changeTab(1);
            }
            this._playing?.refresh();
        }
    }

    render() {
        const isOff = this._entity?.state == "off";
        return html`
            <ha-card>
                ${this._renderBackground()}
                <div class="header">
                    <div class="icon-container" @click=${this._togglePower}>
                        ${this._renderIcon()}
                    </div>
                    <div class="info-container">
                        ${this._renderPrimary()} ${this._renderSecondary()}
                    </div>
                    <div class="action-container">
                        ${this._renderSourceSelector()}
                    </div>
                </div>
                <div class="content">
                    ${!isOff
                        ? html`
                            <polr-media-control
                                id="mediaControl"
                                .hass=${this._hass}
                                .entity=${this._entity}
                            >
                            </polr-media-control>
                            <polr-tab-bar
                                activeIndex=${this._activeTab}
                                @MDCTabBar:activated="${(ev) => this._changeTab(ev.detail.index)}"
                            >
                                <polr-tab label="Playing"></polr-tab>
                                <polr-tab label="For You"></polr-tab>
                            </polr-tab-bar>
                        `
                        : nothing}
                    ${this._renderTab()}
                </div>
            </ha-card>
        `;
    }

    _renderBackground() {
        const attrs = this._entity?.attributes || {};
        let imgUrl = attrs.entity_picture_local || attrs.entity_picture || '';
        return html`
            <div
                class="background"
                style="
                    background: linear-gradient(
                        to top, var(--card-background-color) 50%, 
                        rgba(var(--rgb-card-background-color),0.75) 100%), 
                        url('${imgUrl}')
                        no-repeat;
                    background-size: contain;
                    transition: background 2s ease-in-out;
                "
            ></div>
        `;
    }

    _renderIcon() {
        const attrs = this._entity?.attributes || {};
        if (attrs.entity_picture_local) {
            return html`<img src="${attrs.entity_picture_local}" />`;
        }
        if (attrs.entity_picture) {
            return html`<img src="${attrs.entity_picture}" />`;
        }
        if (this._entity?.state == "off") {
            return html`<ha-icon icon="mdi:speaker"></ha-icon>`;
        }
        return html`<ha-icon icon="${this._config.icon}"></ha-icon>`;
    }

    _renderPrimary() {
        const attrs = this._entity?.attributes || {};
        if (attrs.media_title) {
            return html`<div class="primary">${attrs.media_title}</div>`;
        }
        return html`<div class="primary">${this._config.header}</div>`;
    }

    _renderSecondary() {
        const attrs = this._entity?.attributes || {};
        if (attrs.media_artist) {
            return html`<div class="secondary">${attrs.media_artist}</div>`;
        }
        return html``;
    }

    _renderSourceSelector() {
        if (!this._hass || !this._config) return html``;
        
        const mediaPlayers = [];
        const states = this._hass.states || {};
        const configSpeakers = this._config.speakers || [];
        
        for (const [key, value] of Object.entries(states)) {
            if (key.startsWith("media_player")) {
                const attrs = value?.attributes || {};
                if (attrs.remote_player_id) continue;
                if (configSpeakers.length > 0 && !configSpeakers.includes(key)) continue;
                mediaPlayers.push([key, attrs.friendly_name || key]);
            }
        }
        
        mediaPlayers.sort((a, b) => a[1].localeCompare(b[1]));
        
        const attrs = this._entity?.attributes || {};
        const currentSource = attrs.remote_player_id;
        
        return html`
            <div class="source" style="position: relative;">
                <mwc-icon-button
                    id="sourceSelectorButton"
                    @click=${() => this._sourceSelectorMenu?.show()}
                >
                    ${CastAudioIcon}
                </mwc-icon-button>
                <mwc-menu
                    id="sourceSelectorMenu"
                    @selected=${this._selectSource}
                    .anchor=${this._sourceSelectorButton}
                    corner="BOTTOM_END"
                    menuCorner="END"
                    naturalmenuwidth
                    fixed
                >
                    ${mediaPlayers.map((item) => {
                        const isSelected = item[0] == currentSource;
                        return html`
                            <mwc-list-item
                                ?selected=${isSelected}
                                ?activated=${isSelected}
                                value=${item[0]}
                            >
                                ${item[1]}
                            </mwc-list-item>
                        `;
                    })}
                </mwc-menu>
            </div>
        `;
    }

    _renderTab() {
        const isPlaying = this._activeTab == 0;
        const isForYou = this._activeTab == 1;
        
        return html`
            <zingmp3-playing
                class="${isPlaying ? 'activeTab' : 'hiddenTab'}"
                id="playing"
                ._hass=${this._hass}
                ._entity=${this._entity}
            ></zingmp3-playing>
            <zingmp3-browser
                class="${isForYou ? 'activeTab' : 'hiddenTab'}"
                .hass=${this._hass}
                .entity=${this._entity}
                .initialAction=${this._config.initialAction}
                .coverNavigation=${this._config.coverNavigation}
            ></zingmp3-browser>
        `;
    }

    async _changeTab(index) {
        this._activeTab = index;
        if (index == 0) {
            this._playing?.refresh();
        }
        this.requestUpdate();
    }

    async _selectSource() {
        if (!this._sourceSelectorMenu) return;
        const selectedSource = this._sourceSelectorMenu.selected?.value;
        const attrs = this._entity?.attributes || {};
        const currentSource = attrs.remote_player_id;
        
        if (!selectedSource || selectedSource == currentSource) return;
        
        await this._callService("media_player", "select_source", {
            entity_id: this._config.entity_id,
            source: selectedSource,
        });
    }

    async _togglePower() {
        await this._callService("media_player", "turn_off", {
            entity_id: this._config.entity_id,
        });
        this.requestUpdate();
    }

    async _callService(domain, service, data) {
        try {
            if (!this._hass) {
                console.error('No hass instance available');
                return;
            }
            return await this._hass.callService(domain, service, data);
        } catch (e) {
            console.error(`Error calling ${domain}.${service}:`, e);
            throw e;
        }
    }

    static get styles() {
        return [
            css`
                ha-card {
                    height: 700px;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    transition: filter 0.8s ease 0s;
                }

                .header {
                    position: relative;
                    display: grid;
                    grid-template-columns: 40px auto min-content;
                    padding: 12px 12px 0 12px;
                    gap: 12px;
                    align-items: center;
                }

                .icon-container {
                    display: flex;
                    height: 40px;
                    width: 40px;
                    border-radius: 50%;
                    background: rgba(111, 111, 111, 0.2);
                    place-content: center;
                    align-items: center;
                }

                .icon-container > img {
                    width: 40px;
                    height: 40px;
                    border-radius: 5%;
                    cursor: pointer;
                }

                .info-container {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }

                .primary {
                    font-weight: bold;
                }

                .secondary {
                    font-size: 12px;
                }

                .action-container {
                    display: flex;
                    justify-content: flex-end;
                }

                .content {
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    flex-grow: 1;
                    overflow: auto;
                    gap: 12px;
                    padding: 12px;
                }

                .hiddenTab {
                    display: none;
                }

                #playing {
                    overflow: auto;
                }

                zingmp3-browser {
                    display: flex;
                    flex-grow: 1;
                    overflow: auto;
                }
            `,
        ];
    }
}
customElements.define("zingmp3-playing-card", PoLRYTubePlayingCard);

// ============================================
// COMPONENT: PoLRYTubeSearchCard
// ============================================

class PoLRYTubeSearchCard extends LitElement {
    static get properties() {
        return {
            _config: { type: Object },
            _hass: { type: Object },
            _entity: { type: Object, state: true },
            _runOnce: { type: Boolean, state: true },
        };
    }

    constructor() {
        super();
        this._config = {};
        this._runOnce = false;
        this._entity = null;
        this._hass = null;
    }

    static getConfigElement() {
        return null;
    }

    static getStubConfig() {
        return {};
    }

    setConfig(config) {
        if (!config.entity_id) {
            throw new Error("entity_id must be specified");
        }
        this._config = structuredClone(config);
        if (!("header" in this._config)) {
            this._config.header = "Zing Mp3 Music Search";
        }
        if (!("showHeader" in this._config)) {
            this._config.showHeader = false;
        }
        if (!("icon" in this._config)) {
            this._config.icon = "mdi:speaker";
        }
    }

    set hass(hass) {
        if (!this._runOnce && hass) {
            this._hass = hass;
            this._entity = structuredClone(this._hass?.states?.[this._config?.entity_id]);
            this._runOnce = true;
            this.requestUpdate();
        }
    }

    render() {
        const header = this._config?.showHeader
            ? html`
                <div class="header">
                    <div class="icon-container">
                        <ha-icon icon="${this._config.icon}"></ha-icon>
                    </div>
                    <div class="info-container">
                        <div class="primary">${this._config.header}</div>
                    </div>
                </div>
            `
            : html``;
        
        return html`
            <ha-card>
                ${header}
                <div class="content">
                    <zingmp3-search
                        ._hass=${this._hass}
                        ._entity=${this._entity}
                    >
                    </zingmp3-search>
                </div>
            </ha-card>
        `;
    }

    static get styles() {
        return css`
            ha-card {
                overflow: hidden;
            }

            .header {
                display: grid;
                height: 40px;
                padding: 12px 12px 0 12px;
                grid-template-columns: min-content auto 40px;
                gap: 4px;
            }

            .icon-container {
                display: flex;
                height: 40px;
                width: 40px;
                border-radius: 50%;
                background: rgba(111, 111, 111, 0.2);
                place-content: center;
                align-items: center;
                margin-right: 12px;
            }

            .info-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .primary {
                font-weight: bold;
            }

            .action-container {
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
            }

            .content {
                padding: 12px 12px 12px 12px;
            }
        `;
    }
}
customElements.define("zingmp3-search-card", PoLRYTubeSearchCard);

// ============================================
// COMPONENT: PoLRYTubeSearch
// ============================================

class PoLRYTubeSearch extends LitElement {
    static get properties() {
        return {
            _hass: { type: Object, state: true },
            _entity: { type: Object, state: true },
            _limit: { type: Number },
            _elements: { type: Array, state: true },
        };
    }

    constructor() {
        super();
        this._hass = null;
        this._entity = null;
        this._limit = 25;
        this._elements = [];
        this._polrYTubeBrowser = null;
        this._searchTextField = null;
        this.initialAction = null;
    }

    firstUpdated(_changedProperties) {
        this._polrYTubeBrowser = this.renderRoot.querySelector("zingmp3-browser");
        this._searchTextField = this.renderRoot.querySelector("#query");
    }

    render() {
        return html`
            <div class="content">
                <div class="search">
                    <mwc-textfield
                        label="Search"
                        type="search"
                        id="query"
                        outlined
                        @keyup="${this._handleKey}"
                    >
                    </mwc-textfield>
                    <mwc-select
                        id="filter"
                        label="Filter"
                        fixedMenuPosition
                        naturalMenuWidth
                    >
                        <mwc-list-item value="all">All</mwc-list-item>
                        <mwc-list-item value="artists">Artists</mwc-list-item>
                        <mwc-list-item selected value="songs">
                            Songs
                        </mwc-list-item>
                        <mwc-list-item selected value="playlists">
                            Playlists
                        </mwc-list-item>
                    </mwc-select>
                </div>
                <div class="results">
                    <zingmp3-browser
                        .hass=${this._hass}
                        .entity=${this._entity}
                        .initialAction=${this.initialAction}
                    >
                    </zingmp3-browser>
                </div>
            </div>
        `;
    }

    async _fetchResults() {
        if (!this._hass || !this._entity) return;
        
        try {
            const response = await this._hass.callWS({
                type: "media_player/browse_media",
                entity_id: this._entity?.entity_id,
                media_content_type: "search",
                media_content_id: "",
            });
            
            if (response?.children?.length > 0) {
                response.children = response.children.filter(
                    (el) => !el.media_content_id?.startsWith("MPSP")
                );
                this._elements = response;
                this._polrYTubeBrowser?.loadElement(response);
                this.requestUpdate();
            }
        } catch (e) {
            console.error(e);
        }
    }

    _handleKey(ev) {
        if (ev.keyCode == 13) {
            this._search();
            this._searchTextField?.blur();
        }
    }

    async _search() {
        if (!this._hass || !this._entity) return;
        
        const query = this.shadowRoot?.querySelector("#query")?.value;
        if (!query || query.trim() === '') return;
        
        const filter = this.renderRoot?.querySelector("#filter")?.selected?.value || 'songs';
        const data = {
            entity_id: this._entity.entity_id,
            query: query,
            limit: this._limit,
        };
        if (filter !== "all") {
            data.filter = filter;
        }
        
        await this._hass.callService("zingmp3_player", "search", data);
        this._fetchResults();
    }

    static get styles() {
        return css`
            .search {
                display: grid;
                grid-template-columns: 1fr min-content;
                align-items: center;
                gap: 4px;
            }
        `;
    }
}
customElements.define("zingmp3-search", PoLRYTubeSearch);

// ============================================
// REGISTER CUSTOM CARDS
// ============================================

// Register with Home Assistant card picker
window.customCards = window.customCards || [];
window.customCards.push({
    type: "zingmp3-playing-card",
    name: "Zing Mp3 Playing",
    description: "Requires the zingmp3_media_player integration",
});

window.customCards.push({
    type: "zingmp3-search-card",
    name: "Zing Mp3 Search",
    description: "Requires the zingmp3_media_player integration",
});

// ============================================
// POLYFILLS (nếu cần)
// ============================================

// Ensure LitElement is available globally
if (typeof window.LitElement === 'undefined') {
    // Sử dụng LitElement từ HA
    window.LitElement = window.LitElement || class extends HTMLElement {};
}

// Ensure html và css available
if (typeof window.html === 'undefined') {
    window.html = (strings, ...values) => {
        return String.raw({ raw: strings }, ...values);
    };
}
if (typeof window.css === 'undefined') {
    window.css = (strings, ...values) => {
        return String.raw({ raw: strings }, ...values);
    };
}
