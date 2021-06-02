using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace Licenta.Models
{
    public class Sudoku
    {
        public List<double> Grid { get; set; }
        public List<bool> Original { get; set; }
    }
}