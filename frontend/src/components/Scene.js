import {useLoader} from "@react-three/fiber";
import {OBJLoader} from "three/examples/jsm/loaders/OBJLoader";
import {useTexture} from "@react-three/drei";
import React, {useMemo} from "react";
import mesh from "../texturedMesh.obj";


/*
HOW TO DISPLAY SCENE

<Canvas style={{ maxHeight: '65vh'}}>
    <Suspense fallback={null}>
        <Scene model={this.state.model} texture={this.state.texture}/>
        <OrbitControls />
        <Environment preset="sunset" background />
    </Suspense>
</Canvas>
 */


const Scene = (props) => {
    const obj = useLoader(OBJLoader, props.model);
    const texture = useTexture(props.texture);//useLoader(TextureLoader, props.texture);
    console.log(props.model);
    const geometry = useMemo(() => {
        let g;
        obj.traverse((c) => {
            if (c.type === "Mesh") {
                g = c.geometry;
            }
        });
        return g;
    }, [obj]);

    return (
        <mesh geometry={geometry} scale={1}>
            <meshPhysicalMaterial map={texture} />
        </mesh>
    );
};

export default Scene;