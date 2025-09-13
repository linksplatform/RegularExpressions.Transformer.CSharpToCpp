namespace Platform.Ranges
{
    public struct Range<T>
    {
        public T Minimum { get; set; }
        public T Maximum { get; set; }
        
        public override int GetHashCode()
        {
            return {Minimum, Maximum}.GetHashCode();
        }
    }
}