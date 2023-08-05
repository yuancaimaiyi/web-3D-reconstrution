import Dexie from 'dexie';

export const db = new Dexie('imageStore');

db.version(1).stores({
        images: 'id, src, name'
    });