import langchain_community

langchain_community.document_loaders

def extract_text_from_file(file_path):
    file_name = file_path.split("/")[-1]
    file_type = file_name.split(".")[-1]
    if file_type == "pdf":
        loader = langchain_community.document_loaders.PyPDFLoader(file_path)
    else:
        return df

    text = ""
    pages = loader.load_and_split()
    for page in pages:
        text += page.page_content
    # # Create a new df and concatenate
    # new_row = pd.DataFrame({"file": [file_name], "text": [text]})
    # df = pd.concat([df, new_row], ignore_index=True)
    
    # return df


