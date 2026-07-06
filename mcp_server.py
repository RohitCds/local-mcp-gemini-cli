from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name = "mcp_read_document",
    description = "Reads a document and returns its contents.",
)
def mcp_read_document(
    doc_id: str = Field(description="The ID of the document to read.")
):
    return docs.get(doc_id, f"Document with id {doc_id} not found.")


@mcp.tool(
    name="mcp_edit_document",
    description="Overwrites or updates a document's total content with new text.",
)
def mcp_edit_document(
    doc_id: str = Field(description="The ID of the document to edit."),
    content: str = Field(description="The full, updated content to write into the document.")
):
    if doc_id in docs:
        docs[doc_id] = content
        return f"Successfully updated {doc_id}."
    else:
        return f"Document with id {doc_id} not found."

@mcp.resource(
    "docs://documents",
    mime_type="application/json",
    description="Lists all available document IDs.",
)
def mcp_list_documents():
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
    description="Returns the contents of a particular document.",
)
def mcp_get_document(doc_id: str):
    return docs.get(doc_id, f"Document with id {doc_id} not found.")

# TODO: Write a prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

CRITICAL INSTRUCTION: Even if the extension is .pdf or .docx, you MUST use the 'mcp_read_document' tool first to extract its plain text contents from the server. Do not ask the user to provide or paste the text.

Add in headers, bullet points, tables, etc as necessary to make it clean and readable. 
Use the 'mcp_edit_document' tool to save the updated text back to the server file structure once you finish formatting.
"""
    
    return [
        base.UserMessage(prompt)
    ]

# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
