import numpy as np
from pymesh import tetgen


def reduce_mesh_resolution(mesh, detail="normal"):
    bbox_min, bbox_max = mesh.bbox
    diag_len = np.linalg.norm(bbox_max - bbox_min)

    if detail == "high":
        target_len = diag_len * 1/400
    elif detail == "normal":
        target_len = diag_len * 1/200
    elif detail == "low":
        target_len = diag_len * 1/100
    else:
        raise ValueError

    print("Target resolution: {} mm".format(target_len))

    count = 0
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6)
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                                               preserve_feature=True)
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        print("#v: {}".format(num_vertices))
        count += 1
        if count > 10:
            break

    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    return mesh
