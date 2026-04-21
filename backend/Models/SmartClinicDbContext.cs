using Microsoft.EntityFrameworkCore;

namespace Round2.Models
{
    public class SmartClinicDbContext : DbContext
    {
        public SmartClinicDbContext(DbContextOptions<SmartClinicDbContext> options) : base(options)
        {
        }

        // Define your DbSets here
        // Example:
        // public DbSet<YourModel> YourModels { get; set; }
    }
}