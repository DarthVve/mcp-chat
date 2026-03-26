from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Tool to read a doc
@mcp.tool(name="read_doc", description="Read the contents of a document")
def read_doc(doc_id: str=Field(description="The ID of the document to read")) -> str:
    return docs.get(doc_id, f"Document not found: {doc_id}")

# Tool to edit a doc
@mcp.tool(name="edit_doc", description="Edit the contents of a document")
def edit_doc(doc_id: str=Field(description="The ID of the document to edit"), new_content: str=Field(description="The new content for the document")) -> str:
    if doc_id in docs:
        docs[doc_id] = new_content
        return "Document updated successfully"
    else:
        raise ValueError(f"Document not found: {doc_id}")

# Resource to return all doc id's
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs()-> list[str]:
    return list(docs.keys())

# Resource to return the contents of a particular doc
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def get_doc(doc_id: str=Field(description="The ID of the document to retrieve")) -> str:
    return docs.get(doc_id, f"Document not found: {doc_id}")

@mcp.prompt(name="format_doc", description="Rewrites the contents of the document in Markdown format")
def format_doc(doc_id: str=Field(description="The ID of the document to format")) -> list[base.Message]:
    prompt = f"""
    Your goal is to rewrite the contents of the document with the given ID in Markdown syntax.
    The id of the documnent is {doc_id}.
    Add in headers, bullet points, or any other formatting you think is appropriate based on the content of the document.
    use the read_doc tool to read the contents of the document, then rewrite it in Markdown format using the edit_doc tool and return the reformatted document and save it.
    """
    return [base.UserMessage(prompt)]

@mcp.prompt(name="summarize_doc", description="Summarizes the contents of the document in a few sentences")
def summarize_doc(doc_id: str=Field(description="The ID of the document to summarize")) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize the contents of the document with the given ID in a few sentences.
    The id of the documnent is {doc_id}.
    use the read_doc tool to read the contents of the document, then summarize it in a few sentences and return the summary.
    """
    return [base.UserMessage(prompt)]

if __name__ == "__main__":
    mcp.run(transport="stdio")
