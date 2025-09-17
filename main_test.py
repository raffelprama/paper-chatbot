from server.utils.qdrant.qdrant_remove import clear_collection
from server.utils.qdrant.qdrant_read import read_collection
from server.utils.qdrant.qdrant_insert import insert_collection


# if __name__ == "__main__":
#     data = insert_collection("/mnt/d/user/Downloads/__administartion/Arcfusion/task/resource/papers/")
#     print(data)

# if __name__ == "__main__":
#     data = read_collection()
#     print(data)



from IPython.display import display, Image
from server.src.agent.agent import build_graph

# display(Image(build_graph.get_graph().draw_mermaid_png()))

if __name__ == "__main__":

    import asyncio
    async def main():
        graph = await build_graph()
        png_bytes = graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_bytes)
        print("✅ Graph written to graph.png")

    asyncio.run(main())

    # print(data)

