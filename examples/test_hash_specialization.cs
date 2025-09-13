namespace Platform.Ranges
{
    public struct Range<T>
    {
        public T Minimum;
        public T Maximum;
        
        public override int GetHashCode()
        {
            return {Minimum, Maximum}.GetHashCode();
        }
    }
}