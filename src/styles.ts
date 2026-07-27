import { css } from "lit";

export const styles = css`
:host {
  display: block;
}

ha-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 18px;
  background: var(--ha-card-background, var(--card-background-color));
  transition: all .25s ease;
}

.background {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: blur(28px);
  opacity: .18;
  transform: scale(1.2);
  pointer-events: none;
}

.content {
  position: relative;
  z-index: 1;
}

.header {
  display: flex;
  align-items: center;
  gap: 18px;
}

.cover {
  width: 120px;
  height: 120px;
  border-radius: 14px;
  object-fit: cover;
  background: rgba(255,255,255,.08);
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  font-size: 22px;
  font-weight: 700;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.artist {
  margin-top: 6px;
  color: var(--secondary-text-color);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.progress {
  margin-top: 20px;
}

.time {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 12px;
  color: var(--secondary-text-color);
}

.controls {
  margin-top: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 18px;
}

.play {
  --mdc-icon-size: 42px;
}

.volume {
  margin-top: 20px;
}

ha-slider {
  width: 100%;
}

.search {
  margin-top: 22px;
}

.search ha-textfield {
  width: 100%;
}

.results {
  margin-top: 12px;
  max-height: 320px;
  overflow-y: auto;
}

.result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background .2s;
}

.result:hover {
  background: rgba(255,255,255,.08);
}

.result img {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  object-fit: cover;
}

.result-title {
  font-weight: 600;
}

.result-artist {
  font-size: 13px;
  color: var(--secondary-text-color);
}

@media (max-width:700px){

.header{

flex-direction:column;

text-align:center;

}

.cover{

width:180px;

height:180px;

}

.controls{

gap:12px;

}

}
`;
