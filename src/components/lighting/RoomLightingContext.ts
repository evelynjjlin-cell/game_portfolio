import { createContext } from 'react';
/** Each room shares one physical fill between its pendant and interactive reading lantern. */
export const RoomLightingContext=createContext<{setOn:(on:boolean)=>void;active:boolean;hovered:boolean}|null>(null);
