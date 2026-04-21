using Microsoft.AspNetCore.Mvc;

namespace Round2.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class LLMController : ControllerBase
    {
        [HttpPost("query")]
        public IActionResult QueryLLM([FromBody] LLMRequest request)
        {
            // Placeholder: Call the LLM logic here
            var response = new { Result = $"Response for query: {request.Query}" };
            return Ok(response);
        }
    }

    public class LLMRequest
    {
        public required string Query { get; set; }
    }
}