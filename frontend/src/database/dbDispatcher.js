import {db} from "./db";

class DbDispatcher {
    addImage = async (image) => {
        try {
            const id = await db.images.add(image);
        } catch(error) {
            console.log(error);
        }
    }

    deleteImage = async (id) => {
        try {
            const result = await db.images.delete(id);
        } catch (error) {
            console.log(error);
        }
    }

    updateImage = async (image) => {
        try {
            const result = await db.images.update(image.id, image);
        } catch (error) {
            console.log(error);
        }
    }

    getImages = async () => {
        return await db.images.toArray();
    }

    deleteAllImages = async () => {
        return await db.images.clear();
    }
}

export default DbDispatcher;
